# Cisco Packet Tracer smart-campus demonstration

The editable [campus topology](../topology/AURA-UDP-campus.pkt) contains the routed network and traffic-generator PCs. A PC0-to-Server0 simple ICMP PDU succeeded after ARP learning in Packet Tracer 9.0. Native IoT gateway and sensor registration and HTTP have not yet been completed. Packet Tracer demonstrates connectivity and the campus scenario; it does not execute AURA-UDP.

## Devices and cabling

The saved topology uses two 2911 routers (Router0 and Router1), two 2960 switches (Switch0 and Switch1), one Server-PT (Server0), three PC-PT devices (PC0/1/2, representing temperature, smoke and alert *traffic generators*), and one operations PC (PC3). The PCs and server connect to switches with copper straight-through cables. Switch0 connects to Router0 Gi0/0, Router0 Gi0/1 connects to Router1 Gi0/0, and Router1 Gi0/1 connects to Switch1. To extend the file with native IoT devices, add a Home Gateway, Temperature Meter and Smoke Detector. Connect the gateway Internet port to Switch0 and join the sensors to its IoT wireless network. Cisco's [Packet Tracer IoT activity](https://contenthub.netacad.com/legacy/I2IoT/2.0/en/course/files/1.2.2.1%20Packet%20Tracer%20-%20Adding%20IoT%20Devices%20to%20a%20Smart%20Home.pdf) documents those supported device types and registration workflow.

## Address plan

| Segment | Network | Router | Hosts |
|---|---|---|---|
| Sensors and alerts | 10.10.10.0/24 | R1 Gi0/0 10.10.10.1 | TEMP .11, SMOKE .12, ALERT .13, IOT-GW Internet .2 |
| Transit | 10.10.20.0/30 | Router0 Gi0/1 .1, Router1 Gi0/0 .2 | — |
| Server and operations | 10.10.30.0/24 | Router1 Gi0/1 10.10.30.1 | MONITOR .10, OPS .11 |

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

On Router1 use Gi0/1 `10.10.30.1 255.255.255.0`, Gi0/0 `10.10.20.2 255.255.255.252`, and `ip route 10.10.10.0 255.255.255.0 10.10.20.1`.

## Verification and scenario

1. Confirm `show ip interface brief` shows all router links up/up and `show ip route` includes the remote LAN.
2. From TEMP, SMOKE, and ALERT, ping `10.10.30.10`; from OPS ping `10.10.10.13`.
3. Enable HTTP on MONITOR in Services, then open `http://10.10.30.10` from OPS. This confirms application connectivity.
4. In Simulation mode filter ICMP and HTTP. Send periodic simple PDUs from TEMP and SMOKE to MONITOR as routine telemetry; send an immediate PDU from ALERT as the critical-alert scenario. Record packet paths and timestamps as demonstration evidence.
5. Check the Temperature Meter value and Smoke Detector status in the Home Gateway IoT device page. Trigger a smoke event using the device's supported controls and record the status change. Device control labels can differ between Packet Tracer builds.

Packet Tracer simple PDUs do not model custom UDP reliability, retransmission deadlines, or the NS2 traffic generator. The NS2 topology mirrors the two-ended routed path at a logical level, with an additional background sender to stress the bottleneck.
