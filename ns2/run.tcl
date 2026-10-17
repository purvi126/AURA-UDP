# AURA-UDP: OTcl transport running over real NS2 Message agents and links.
# ns run.tcl MODE LOSS DELAY_MS BACKGROUND_KBPS DEADLINE_MS SEED OUTDIR
#   ?INTERVAL_MS? ?POLICY? ?MESSAGE_COUNT? ?BACKGROUND_SOURCES? ?QUEUE_LIMIT?
#   ?regular|burst_late_alert? ?BOTTLENECK_KBPS?
if {$argc < 7 || $argc > 14} { puts stderr "usage: ns run.tcl baseline|sr|aura loss delay_ms background_kbps deadline_ms seed outdir ?interval_ms? ?full|no_feasibility|fixed_window|legacy|reserved_alert_slot? ?message_count? ?background_sources? ?queue_limit? ?regular|burst_late_alert? ?bottleneck_kbps?"; exit 2 }
lassign $argv mode loss delay_ms bg_kbps deadline_ms seed outdir interval_ms policy message_count bg_sources queue_limit schedule bottleneck_kbps
if {$interval_ms eq ""} { set interval_ms 120 }
if {$policy eq ""} { set policy full }
if {$message_count eq ""} { set message_count 30 }
if {$bg_sources eq ""} { set bg_sources 1 }
if {$queue_limit eq ""} { set queue_limit 12 }
if {$schedule eq ""} { set schedule regular }
if {$bottleneck_kbps eq ""} { set bottleneck_kbps 128 }
if {$mode ni {baseline sr aura}} { error "invalid mode $mode" }
if {$policy ni {full no_feasibility fixed_window legacy reserved_alert_slot}} { error "invalid policy $policy" }
if {$mode ne "aura" && $policy ne "full"} { error "policy variants require aura mode" }
if {$schedule ni {regular burst_late_alert}} { error "invalid schedule $schedule" }
foreach {name value} [list loss $loss delay_ms $delay_ms background_kbps $bg_kbps deadline_ms $deadline_ms interval_ms $interval_ms] {
    if {![regexp {^(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$} $value]} { error "$name must be a non-negative finite number" }
}
if {$loss > 1} { error "loss must be between 0 and 1" }
if {$delay_ms <= 0 || $deadline_ms <= 0 || $interval_ms <= 0} { error "delay, deadline, and interval must be positive" }
if {![string is integer -strict $seed] || $seed < 0} { error "seed must be a non-negative integer" }
if {![string is integer -strict $message_count] || $message_count < 1} { error "message_count must be a positive integer" }
if {![string is integer -strict $bg_sources] || $bg_sources ni {1 2}} { error "background_sources must be 1 or 2" }
if {![string is integer -strict $queue_limit] || $queue_limit < 1} { error "queue_limit must be a positive integer" }
if {![string is integer -strict $bottleneck_kbps] || $bottleneck_kbps < 1} { error "bottleneck_kbps must be a positive integer" }
if {$schedule eq "burst_late_alert" && $message_count % 4 != 0} { error "burst_late_alert requires message_count divisible by 4" }
if {$outdir eq ""} { error "output directory must not be empty" }
file mkdir $outdir
# The seed is a replication/substream index. Keep data and ACK loss on
# separate RNG streams so their draws do not consume each other's sequence.
ns-random 1
set data_rng [new RNG]
set ack_rng [new RNG]
$data_rng seed 2117
$ack_rng seed 9871
for {set replication 0} {$replication < $seed} {incr replication} {
    $data_rng next-substream
    $ack_rng next-substream
}
set ns [new Simulator]
set trace [open "$outdir/ns2.tr" w]
set nam [open "$outdir/ns2.nam" w]
set events [open "$outdir/events.csv" w]
puts $events "time,event,id,class,attempt,deadline"
set control [open "$outdir/control.csv" w]
puts $control "time,event,window,rto,id"
$ns trace-all $trace
$ns namtrace-all $nam
set src [$ns node]; set router [$ns node]; set dst [$ns node]; set bgsrc [$ns node]
if {$bg_sources == 2} { set bgsrc2 [$ns node] }
set delay "${delay_ms}ms"
$ns duplex-link $src $router 1Mb 2ms DropTail
$ns duplex-link $bgsrc $router 1Mb 2ms DropTail
if {$bg_sources == 2} { $ns duplex-link $bgsrc2 $router 1Mb 2ms DropTail }
$ns duplex-link $router $dst "${bottleneck_kbps}Kb" $delay DropTail
$ns queue-limit $router $dst $queue_limit
set data_loss [new ErrorModel]
$data_loss unit pkt
$data_loss set rate_ $loss
set data_uniform [new RandomVariable/Uniform]
$data_uniform use-rng $data_rng
$data_loss ranvar $data_uniform
$ns lossmodel $data_loss $router $dst
set ack_loss [new ErrorModel]
$ack_loss unit pkt
$ack_loss set rate_ $loss
set ack_uniform [new RandomVariable/Uniform]
$ack_uniform use-rng $ack_rng
$ack_loss ranvar $ack_uniform
$ns lossmodel $ack_loss $dst $router
Class Agent/AuraEndpoint -superclass Agent/Message
Agent/AuraEndpoint instproc recv {payload} {
    global ns events received delivered deadline sender mode
    set f [split $payload :]
    set kind [lindex $f 0]
    set id [lindex $f 1]
    if {$kind eq "ACK"} { on_ack $id; return }
    set cls [lindex $f 2]
    set attempt [lindex $f 3]
    set dl [lindex $f 4]
    set now [$ns now]
    puts $events "$now,receive,$id,$cls,$attempt,$dl"
    if {![info exists received($id)]} {
        set received($id) 1
        set delivered($id) 1
        puts $events "$now,deliver,$id,$cls,$attempt,$dl"
        if {$now > $dl && $cls eq "critical"} {
            puts $events "$now,late,$id,$cls,$attempt,$dl"
        }
    } else { puts $events "$now,duplicate,$id,$cls,$attempt,$dl" }
    if {$mode ne "baseline"} { $self send "ACK:$id" }
}
set sender [new Agent/AuraEndpoint]
set receiver [new Agent/AuraEndpoint]
$ns attach-agent $src $sender
$ns attach-agent $dst $receiver
$ns connect $sender $receiver
$ns connect $receiver $sender
set bga [new Agent/UDP]
set bgs [new Agent/LossMonitor]
$ns attach-agent $bgsrc $bga
$ns attach-agent $dst $bgs
$ns connect $bga $bgs
set cbr [new Application/Traffic/CBR]
$cbr set packetSize_ 200
if {$bg_kbps > 0} { $cbr set rate_ "[expr {$bg_kbps/double($bg_sources)}]Kb" } else { $cbr set rate_ "1Kb" }
$cbr attach-agent $bga
if {$bg_sources == 2} {
    set bga2 [new Agent/UDP]
    set bgs2 [new Agent/LossMonitor]
    $ns attach-agent $bgsrc2 $bga2
    $ns attach-agent $dst $bgs2
    $ns connect $bga2 $bgs2
    set cbr2 [new Application/Traffic/CBR]
    $cbr2 set packetSize_ 200
    if {$bg_kbps > 0} { $cbr2 set rate_ "[expr {$bg_kbps/2.0}]Kb" } else { $cbr2 set rate_ "1Kb" }
    $cbr2 attach-agent $bga2
}
set window 4
set window_credit 0
set rto 0.3
set srtt 0.0
set rttvar 0.0
set nextid 0
array set state {}
array set attempts {}
array set firstsend {}
array set senttime {}
array set class {}
array set deadline {}
array set received {}
array set delivered {}
set pending {}
set critical_streak 0
puts $control "0,init,$window,$rto,0"
proc log_control {event id} {
    global ns control window rto
    puts $control "[$ns now],$event,$window,$rto,$id"
}
proc expected_forward_time {} {
    global delay_ms srtt
    # Symmetric lab links: half the sampled RTT estimates a forward trip.
    # Propagation delay is a floor; the first send is never discarded by this estimate.
    if {$srtt == 0.0} { return [expr {$delay_ms/1000.0}] }
    return [expr {max($delay_ms/1000.0, $srtt/2.0)}]
}
proc log_event {ev id} {
    global ns events class attempts deadline
    puts $events "[$ns now],$ev,$id,$class($id),$attempts($id),$deadline($id)"
}
proc transmit {id} {
    global ns sender mode policy class deadline attempts senttime state rto
    if {$state($id) ne "pending"} { return 0 }
    if {$mode eq "aura" && $class($id) eq "critical" && [$ns now] >= $deadline($id)} {
        set state($id) expired; log_event expire $id; return 0
    }
    if {$mode eq "aura" && $class($id) eq "critical" && $attempts($id) > 0
        && $policy ni {no_feasibility legacy}
        && [$ns now] + [expected_forward_time] > $deadline($id)} {
        set state($id) abandoned; log_event abandon $id; log_control abandon $id; return 0
    }
    incr attempts($id)
    set senttime($id) [$ns now]
    log_event send $id
    $sender send "DATA:$id:$class($id):$attempts($id):$deadline($id)"
    if {$mode ne "baseline"} { $ns at [expr {[$ns now] + $rto}] "timeout $id $attempts($id)" }
    return 1
}
proc expire_alert {id} {
    global state
    if {$state($id) ni {queued pending}} { return }
    set state($id) expired
    log_event expire $id
    pump
}
proc timeout {id attempt} {
    global state attempts mode policy deadline ns rto window window_credit
    if {$state($id) ne "pending" || $attempts($id) != $attempt} { return }
    if {$mode eq "aura" && [$ns now] >= $deadline($id)} {
        set state($id) expired; log_event expire $id; pump; return
    }
    if {$attempts($id) >= 5} { set state($id) failed; log_event fail $id; pump; return }
    log_event timeout $id
    if {$mode eq "aura"} {
        set rto [expr {min(1.0, $rto * 1.5)}]
        if {$policy ni {fixed_window legacy}} {
            set window [expr {max(4, int($window/2))}]
            set window_credit 0
        }
        log_control timeout $id
    }
    if {![transmit $id]} { pump }
}
proc on_ack {id} {
    global ns state mode policy attempts senttime srtt rttvar rto window window_credit
    if {![info exists state($id)] || $state($id) ne "pending"} { return }
    set state($id) acked
    log_event ack $id
    # Karn's rule: only use unambiguous RTT samples.
    if {$mode eq "aura" && $attempts($id) == 1} {
        set sample [expr {[$ns now] - $senttime($id)}]
        if {$srtt == 0.0} { set srtt $sample; set rttvar [expr {$sample / 2.0}] } else {
            set rttvar [expr {0.75*$rttvar + 0.25*abs($srtt-$sample)}]
            set srtt [expr {0.875*$srtt + 0.125*$sample}]
        }
        set rto [expr {max(0.08, min(1.0, $srtt + 4*$rttvar))}]
    }
    if {$mode eq "aura" && $policy ni {fixed_window legacy} && $window < 6} {
        incr window_credit
        if {$window_credit >= $window} {
            incr window
            set window_credit 0
            log_control increase $id
        }
    }
    pump
}
proc pump {} {
    global mode policy pending state class window critical_streak
    if {$mode eq "baseline"} { return }
    set active 0
    foreach id [array names state] { if {$state($id) eq "pending"} { incr active } }
    while {$active < $window && [llength $pending] > 0} {
        set index 0
        if {$mode eq "aura" && $policy ne "legacy" && $critical_streak >= 3
            && !($policy eq "reserved_alert_slot" && $active >= $window - 1)} {
            for {set i 0} {$i < [llength $pending]} {incr i} {
                set candidate [lindex $pending $i]
                if {$state($candidate) eq "queued" && $class($candidate) eq "routine"} {
                    set index $i
                    break
                }
            }
        }
        set id [lindex $pending $index]
        # Keep one admission slot available for the next critical alert.
        # This policy is an experimental variant; it does not change full.
        if {$mode eq "aura" && $policy eq "reserved_alert_slot"
            && $class($id) eq "routine" && $active >= $window - 1} { break }
        set pending [lreplace $pending $index $index]
        if {$state($id) ne "queued"} { continue }
        set state($id) pending
        if {[transmit $id]} {
            incr active
            if {$class($id) eq "critical"} { incr critical_streak } else { set critical_streak 0 }
        }
    }
}
proc generate {cls} {
    global ns nextid deadline_ms state attempts class deadline pending mode policy
    set id [incr nextid]
    set class($id) $cls
    set attempts($id) 0
    if {$cls eq "critical"} { set deadline($id) [expr {[$ns now]+$deadline_ms/1000.0}] } else { set deadline($id) 10000.0 }
    set state($id) queued
    log_event generate $id
    if {$mode eq "aura" && $cls eq "critical"} { $ns at $deadline($id) "expire_alert $id" }
    if {$mode eq "baseline"} { set state($id) pending; transmit $id; return }
    if {$mode eq "aura" && $cls eq "critical"} {
        if {$policy eq "legacy"} {
            set pending [linsert $pending 0 $id]
        } else {
            set index 0
            foreach queued $pending {
                if {$class($queued) ne "critical" || $deadline($queued) > $deadline($id)} { break }
                incr index
            }
            set pending [linsert $pending $index $id]
        }
    } else { lappend pending $id }
    pump
}
proc finish {} {
    global ns trace nam events control bgs bgs2 bg_sources outdir
    puts $events "[$ns now],finish,0,,0,"
    set background [open "$outdir/background.csv" w]
    if {$bg_sources == 2} {
        set flow1_packets [$bgs set npkts_]
        set flow1_bytes [$bgs set bytes_]
        set flow2_packets [$bgs2 set npkts_]
        set flow2_bytes [$bgs2 set bytes_]
        puts $background "time,received_packets,received_bytes,flow1_packets,flow1_bytes,flow2_packets,flow2_bytes"
        puts $background "[$ns now],[expr {$flow1_packets+$flow2_packets}],[expr {$flow1_bytes+$flow2_bytes}],$flow1_packets,$flow1_bytes,$flow2_packets,$flow2_bytes"
    } else {
        puts $background "time,received_packets,received_bytes"
        puts $background "[$ns now],[$bgs set npkts_],[$bgs set bytes_]"
    }
    close $background
    close $trace; close $nam; close $events; close $control
    exit 0
}
if {$bg_kbps > 0} { $ns at 0.05 "$cbr start" }
if {$bg_kbps > 0 && $bg_sources == 2} { $ns at 0.05 "$cbr2 start" }
for {set i 0} {$i < $message_count} {incr i} {
    if {$schedule eq "burst_late_alert"} {
        # Preserve the mean offered load while placing each alert after three
        # closely spaced routine messages. All modes share this exact schedule.
        set t [expr {0.1 + int($i/4)*4*$interval_ms/1000.0 + ($i%4)*0.005}]
        if {$i % 4 == 3} { set cls critical } else { set cls routine }
    } else {
        set t [expr {0.1 + $i*$interval_ms/1000.0}]
        if {$i % 4 == 0} { set cls critical } else { set cls routine }
    }
    $ns at $t "generate $cls"
}
set finish_time [expr {max(6.0, 0.1 + $message_count*$interval_ms/1000.0 + 2.5)}]
if {$bg_kbps > 0} { $ns at [expr {$finish_time - 1.0}] "$cbr stop" }
if {$bg_kbps > 0 && $bg_sources == 2} { $ns at [expr {$finish_time - 1.0}] "$cbr2 stop" }
$ns at $finish_time "finish"
$ns run
