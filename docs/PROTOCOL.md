# Protocol and experiment method

## Scope

NS2 `Agent/Message` instances carry numbered application datagrams through NS2 links, queues and loss models. Both endpoints are implemented in OTcl. The bottleneck is a 128 Kb/s router-to-destination link with a 12-packet DropTail queue; a CBR flow shares it. The return path has an independent packet error model for ACK loss.

## State machine

`queued → pending → acked | failed | expired`. A receive at the destination first records a message ID, then sends an ACK for every copy. Duplicate copies are suppressed. A critical copy arriving after its absolute deadline is marked late but still counted in PDR, never DDR. Its sender can still receive an ACK. The sender keeps up to four unacknowledged messages in flight and retries an individual message when its timer fires, up to five attempts. AURA schedules an expiration event at each critical alert's absolute deadline, so an unacknowledged alert frees its sender window immediately, even if its retry timer is later. An already delivered alert may still expire at the sender if its ACK has not returned by that deadline.

Baseline UDP sends once and does not ACK. Fixed Selective Repeat uses a 300 ms timeout and FIFO admission. AURA uses critical-first admission and an RTT-derived timeout (`SRTT + 4 × RTTVAR`, bounded 80–1000 ms), with 1.5× backoff on timeout. It does not retransmit critical traffic after expiration. RTT samples from retransmitted packets are excluded using Karn's rule. Adaptive window sizing is future work.

These are application-layer reliability mechanisms over NS2 datagram agents. `Agent/Message` is a built-in NS2 transport class, not a custom C++ UDP header implementation. The 64-byte logical payload in goodput is an analysis assumption; actual NS2 packet header sizes may differ.

## Metrics

PDR is unique delivered messages divided by generated messages. DDR is critical messages delivered by their deadline divided by all critical messages generated. Critical-alert success rate currently equals DDR because each critical message represents one alert. Delay is from generation to first delivery, averaged over delivered messages only. Retransmission overhead is `(send events − distinct IDs sent at least once) / generated messages`; queued messages that expire before their first send do not create negative overhead. Throughput is unique delivered messages divided by the interval from the first generation to the common `finish` event. Goodput uses 64 logical bytes per unique delivery over that same interval. Repeated receives or ACKs never add deliveries. Legacy logs without a `finish` event use their last event as a fallback end time and should not be compared to current fixed-window results.

## Limitations

Each run has a fixed 30-message workload. The 30-seed sweep covers three configured scenarios, including a higher generation rate, but remains a short synthetic evaluation rather than a general performance claim. Background CBR has no application event logging. Priority applies to sender admission, not router queue scheduling. Packet Tracer is a separate connectivity demonstration and does not run AURA.
