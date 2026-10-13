# Cisco Packet Tracer smart-campus demonstration

The editable [campus topology](../topology/AURA-UDP-campus.pkt) contains the routed network, traffic-generator PCs, a DLC100 Home Gateway, a Temperature Monitor, and a Smoke Detector. A PC0-to-Server0 simple ICMP PDU succeeded after ARP learning, and Server0's HTTP page loaded from PC3 in Packet Tracer 9.0. The sensors are wirelessly associated and configured to use Home Gateway as their IoT server; registered-device-list inspection remains open. Packet Tracer demonstrates connectivity and the campus scenario; it does not execute AURA-UDP.

## Devices and cabling

The saved topology uses two 2911 routers (Router0 and Router1), two 2960 switches (Switch0 and Switch1), one Server-PT (Server0), three PC-PT devices (PC0/1/2, representing temperature, smoke and alert *traffic generators*), one operations PC (PC3), and a wireless tablet (Tablet PC0). The PCs and server connect to switches with copper straight-through cables. Switch0 connects to Router0 Gi0/0, Router0 Gi0/1 connects to Router1 Gi0/0, and Router1 Gi0/1 connects to Switch1. The Home Gateway Internet port connects to Switch0; the native Temperature Monitor, Smoke Detector, and tablet use its wireless network. Cisco's [Packet Tracer IoT activity](https://contenthub.netacad.com/legacy/I2IoT/2.0/en/course/files/1.2.2.1%20Packet%20Tracer%20-%20Adding%20IoT%20Devices%20to%20a%20Smart%20Home.pdf) documents the registration workflow.

## Address plan

| Segment | Network | Router | Hosts |
|---|---|---|---|
| Sensors and alerts | 10.10.10.0/24 | Router0 Gi0/0 10.10.10.1 | PC0 .11, PC1 .12, PC2 .13, HomeGateway0 Internet .2 |
| Transit | 10.10.20.0/30 | Router0 Gi0/1 .1, Router1 Gi0/0 .2 | — |
| Server and operations | 10.10.30.0/24 | Router1 Gi0/1 10.10.30.1 | MONITOR .10, OPS .11 |

Set each host's mask to 255.255.255.0 and default gateway to its local router address.

HomeGateway0 has Internet address `10.10.10.2/24` and gateway `10.10.10.1`. Its internal IoT subnet is `192.168.25.0/24`. The native devices are named TEMP-SENSOR and SMOKE-SENSOR; both show wireless association, use static internal addresses `192.168.25.11` and `192.168.25.12`, and select Home Gateway as their IoT server. Tablet PC0 uses SSID HomeGateway and static address `192.168.25.20` because its DHCP request failed in this saved lab. It can load the gateway login page at `http://192.168.25.1`. The registered-device list was empty when checked before static sensor addressing; it needs to be rechecked after that change. The gateway Internet address timed out from PC3's browser, so that path does not verify registration.

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
3. Server0 HTTP is On. Open `http://10.10.30.10` from PC3 to reproduce the verified page load.
4. In Simulation mode filter ICMP and HTTP. Send periodic simple PDUs from TEMP and SMOKE to MONITOR as routine telemetry; send an immediate PDU from ALERT as the critical-alert scenario. Record packet paths and timestamps as demonstration evidence.
5. Check the Temperature Monitor value and Smoke Detector status in the Home Gateway IoT device page. Trigger a smoke event using the device's supported controls and record the status change. Device control labels can differ between Packet Tracer builds.

Packet Tracer simple PDUs do not model custom UDP reliability, retransmission deadlines, or the NS2 traffic generator. The NS2 topology mirrors the two-ended routed path at a logical level, with an additional background sender to stress the bottleneck.
