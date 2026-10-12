# AURA-UDP: OTcl transport running over real NS2 Message agents and links.
# ns run.tcl MODE LOSS DELAY_MS BACKGROUND_KBPS DEADLINE_MS SEED OUTDIR ?INTERVAL_MS?
if {$argc != 7 && $argc != 8} { puts stderr "usage: ns run.tcl baseline|sr|aura loss delay_ms background_kbps deadline_ms seed outdir ?interval_ms?"; exit 2 }
lassign $argv mode loss delay_ms bg_kbps deadline_ms seed outdir interval_ms
if {$interval_ms eq ""} { set interval_ms 120 }
if {$mode ni {baseline sr aura}} { error "invalid mode $mode" }
file mkdir $outdir
ns-random $seed
set ns [new Simulator]
set trace [open "$outdir/ns2.tr" w]
set nam [open "$outdir/ns2.nam" w]
set events [open "$outdir/events.csv" w]
puts $events "time,event,id,class,attempt,deadline"
$ns trace-all $trace
$ns namtrace-all $nam
set src [$ns node]; set router [$ns node]; set dst [$ns node]; set bgsrc [$ns node]
set delay "${delay_ms}ms"
$ns duplex-link $src $router 1Mb 2ms DropTail
$ns duplex-link $bgsrc $router 1Mb 2ms DropTail
$ns duplex-link $router $dst 128Kb $delay DropTail
$ns queue-limit $router $dst 12
set data_loss [new ErrorModel]
$data_loss unit pkt
$data_loss set rate_ $loss
$ns lossmodel $data_loss $router $dst
set ack_loss [new ErrorModel]
$ack_loss unit pkt
$ack_loss set rate_ $loss
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
set bgs [new Agent/Null]
$ns attach-agent $bgsrc $bga
$ns attach-agent $dst $bgs
$ns connect $bga $bgs
set cbr [new Application/Traffic/CBR]
$cbr set packetSize_ 200
if {$bg_kbps > 0} { $cbr set rate_ "${bg_kbps}Kb" } else { $cbr set rate_ "1Kb" }
$cbr attach-agent $bga
set window 4
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
proc log_event {ev id} {
    global ns events class attempts deadline
    puts $events "[$ns now],$ev,$id,$class($id),$attempts($id),$deadline($id)"
}
proc transmit {id} {
    global ns sender mode class deadline attempts senttime state rto
    if {$state($id) ne "pending"} { return }
    if {$mode eq "aura" && $class($id) eq "critical" && [$ns now] >= $deadline($id)} {
        set state($id) expired; log_event expire $id; pump; return
    }
    incr attempts($id)
    set senttime($id) [$ns now]
    log_event send $id
    $sender send "DATA:$id:$class($id):$attempts($id):$deadline($id)"
    if {$mode ne "baseline"} { $ns at [expr {[$ns now] + $rto}] "timeout $id $attempts($id)" }
}
proc timeout {id attempt} {
    global state attempts mode deadline ns rto
    if {$state($id) ne "pending" || $attempts($id) != $attempt} { return }
    if {$mode eq "aura" && [$ns now] >= $deadline($id)} {
        set state($id) expired; log_event expire $id; pump; return
    }
    if {$attempts($id) >= 5} { set state($id) failed; log_event fail $id; pump; return }
    log_event timeout $id
    if {$mode eq "aura"} { set rto [expr {min(1.0, $rto * 1.5)}] }
    transmit $id
}
proc on_ack {id} {
    global ns state mode attempts senttime srtt rttvar rto
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
    pump
}
proc pump {} {
    global mode pending state window
    if {$mode eq "baseline"} { return }
    set active 0
    foreach id [array names state] { if {$state($id) eq "pending"} { incr active } }
    while {$active < $window && [llength $pending] > 0} {
        set id [lindex $pending 0]
        set pending [lrange $pending 1 end]
        set state($id) pending
        transmit $id
        incr active
    }
}
proc generate {cls} {
    global ns nextid deadline_ms state attempts class deadline pending mode
    set id [incr nextid]
    set class($id) $cls
    set attempts($id) 0
    if {$cls eq "critical"} { set deadline($id) [expr {[$ns now]+$deadline_ms/1000.0}] } else { set deadline($id) 10000.0 }
    set state($id) queued
    log_event generate $id
    if {$mode eq "baseline"} { set state($id) pending; transmit $id; return }
    if {$mode eq "aura" && $cls eq "critical"} { set pending [linsert $pending 0 $id] } else { lappend pending $id }
    pump
}
proc finish {} {
    global trace nam events
    close $trace; close $nam; close $events
    exit 0
}
if {$bg_kbps > 0} { $ns at 0.05 "$cbr start" }
for {set i 0} {$i < 30} {incr i} {
    set t [expr {0.1 + $i*$interval_ms/1000.0}]
    if {$i % 4 == 0} { set cls critical } else { set cls routine }
    $ns at $t "generate $cls"
}
set finish_time [expr {max(6.0, 0.1 + 30*$interval_ms/1000.0 + 2.5)}]
if {$bg_kbps > 0} { $ns at [expr {$finish_time - 1.0}] "$cbr stop" }
$ns at $finish_time "finish"
$ns run
