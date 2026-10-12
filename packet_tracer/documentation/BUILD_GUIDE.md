# Cisco Packet Tracer smart-campus demonstration

This is a reproducible network build guide. No `.pkt` file has been created or verified. Packet Tracer demonstrates connectivity and the campus scenario; it does not execute AURA-UDP.

## Devices and cabling

Use two 2911 routers (R1 and R2), two 2960 switches (SW-SENSOR and SW-SERVER), one Server-PT (MONITOR), three PC-PT devices representing telemetry and safety-alert *traffic generators*, one PC-PT (OPS), one Home Gateway (IOT-GW), one Temperature Meter and one Smoke Detector. Connect the PCs and server to their switches with copper straight-through cables. Connect SW-SENSOR Fa0/24 to R1 Gi0/0, R1 Gi0/1 to R2 Gi0/1, and R2 Gi0/0 to SW-SERVER Fa0/24. Connect the Home Gateway Internet port to SW-SENSOR with copper straight-through. Place the Temperature Meter and Smoke Detector on its IoT wireless network. Cisco's [Packet Tracer IoT activity](https://contenthub.netacad.com/legacy/I2IoT/2.0/en/course/files/1.2.2.1%20Packet%20Tracer%20-%20Adding%20IoT%20Devices%20to%20a%20Smart%20Home.pdf) documents those supported device types and registration workflow.

## Address plan

| Segment | Network | Router | Hosts |
|---|---|---|---|
| Sensors and alerts | 10.10.10.0/24 | R1 Gi0/0 10.10.10.1 | TEMP .11, SMOKE .12, ALERT .13, IOT-GW Internet .2 |
| Transit | 10.10.20.0/30 | R1 Gi0/1 .1, R2 Gi0/1 .2 | — |
| Server and operations | 10.10.30.0/24 | R2 Gi0/0 10.10.30.1 | MONITOR .10, OPS .11 |

Set each host's mask to 255.255.255.0 and default gateway to its local router address.

For IOT-GW, configure the Internet-facing address `10.10.10.2/24` and gateway `10.10.10.1` if its selected Packet Tracer model exposes static WAN setup; otherwise reserve `.2` with DHCP on that LAN. Keep the gateway's default internal IoT subnet separate from `10.10.10.0/24`. On each IoT device's Config tab, join the gateway SSID, obtain an internal address by DHCP, and choose Home Gateway as the IoT registration server. Confirm both appear in the Home Gateway's IoT device page. This validates actual sensor registration; the PC traffic generators provide the routed packet demonstration.

## Router configuration

On R1:

```text
enable
configure terminal
interface gigabitEthernet0/0
ip address 10.10.10.1 255.255.255.0
no shutdown
exit
interface gigabitEthernet0/1
ip address 10.10.20.1 255.255.255.252
no shutdown
exit
ip route 10.10.30.0 255.255.255.0 10.10.20.2
end
write memory
```

On R2 use Gi0/0 `10.10.30.1 255.255.255.0`, Gi0/1 `10.10.20.2 255.255.255.252`, and `ip route 10.10.10.0 255.255.255.0 10.10.20.1`.

## Verification and scenario

1. Confirm `show ip interface brief` shows all router links up/up and `show ip route` includes the remote LAN.
2. From TEMP, SMOKE, and ALERT, ping `10.10.30.10`; from OPS ping `10.10.10.13`.
3. Enable HTTP on MONITOR in Services, then open `http://10.10.30.10` from OPS. This confirms application connectivity.
4. In Simulation mode filter ICMP and HTTP. Send periodic simple PDUs from TEMP and SMOKE to MONITOR as routine telemetry; send an immediate PDU from ALERT as the critical-alert scenario. Record packet paths and timestamps as demonstration evidence.
5. Check the Temperature Meter value and Smoke Detector status in the Home Gateway IoT device page. Trigger a smoke event using the device's supported controls and record the status change. Device control labels can differ between Packet Tracer builds.

Packet Tracer simple PDUs do not model custom UDP reliability, retransmission deadlines, or the NS2 traffic generator. The NS2 topology mirrors the two-ended routed path at a logical level, with an additional background sender to stress the bottleneck.
