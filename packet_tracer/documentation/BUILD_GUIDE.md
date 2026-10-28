# Cisco Packet Tracer smart-campus demonstration

The saved topology includes an Old Car named `SMOKE-TRIGGER-CAR` beside the native Smoke Detector in Corporate Office → Main Wiring Closet. A manual Smoke adjustment triggered the detector on 2026-10-29, but the car itself did not produce an observed alarm.

The editable [campus topology](../topology/AURA-UDP-campus.pkt) contains the routed network, traffic-generator PCs, a DLC100 Home Gateway, a Temperature Monitor, and a Smoke Detector. PC0-to-Server0 simple ICMP PDU succeeded after ARP learning. PC1 and PC2 each pinged Server0 successfully, and PC3 pinged PC2 successfully. Sensor-side PC0 loaded the custom [AURA landing page](server-index.html) from Server0 over HTTP through Router0 and Router1 in Packet Tracer 9.0, including after the 2026-10-29 physical move. PC3 also loaded the page, but PC3 and Server0 share the server LAN. An earlier gateway Devices page showed both wireless native sensors; the post-move page listed only `TEMP-SENSOR`. Packet Tracer demonstrates connectivity and the campus scenario; it does not execute AURA-UDP.

## Devices and cabling

The saved topology uses two 2911 routers (Router0 and Router1), two 2960 switches (Switch0 and Switch1), one Server-PT (Server0), three PC-PT devices (PC0/1/2, representing temperature, smoke and alert *traffic generators*), one operations PC (PC3), and a wireless tablet (Tablet PC0). The PCs and server connect to switches with copper straight-through cables. Switch0 connects to Router0 Gi0/0, Router0 Gi0/1 connects to Router1 Gi0/0, and Router1 Gi0/1 connects to Switch1. The Home Gateway Internet port connects to Switch0; the native Temperature Monitor, Smoke Detector, and tablet use its wireless network. Cisco's [Packet Tracer IoT activity](https://contenthub.netacad.com/legacy/I2IoT/2.0/en/course/files/1.2.2.1%20Packet%20Tracer%20-%20Adding%20IoT%20Devices%20to%20a%20Smart%20Home.pdf) documents the registration workflow.

## Address plan

| Segment | Network | Router | Hosts |
|---|---|---|---|
| Sensors and alerts | 10.10.10.0/24 | Router0 Gi0/0 10.10.10.1 | PC0 .11, PC1 .12, PC2 .13, HomeGateway0 Internet .2 |
| Transit | 10.10.20.0/30 | Router0 Gi0/1 .1, Router1 Gi0/0 .2 | — |
| Server and operations | 10.10.30.0/24 | Router1 Gi0/1 10.10.30.1 | MONITOR .10, OPS .11 |

Set each host's mask to 255.255.255.0 and default gateway to its local router address.

HomeGateway0 has Internet address `10.10.10.2/24` and gateway `10.10.10.1`. Its internal IoT subnet is `192.168.25.0/24`. The native devices are named TEMP-SENSOR and SMOKE-SENSOR; earlier checks showed wireless association, static internal addresses `192.168.25.11` and `192.168.25.12`, and Home Gateway as their IoT server. Tablet PC0 uses SSID HomeGateway and static address `192.168.25.20` because its DHCP request failed in this saved lab. At `http://192.168.25.1`, the gateway's Devices page previously listed both sensors and exposed the temperature and smoke-level fields. On 2026-10-29, the refreshed post-move Devices page listed only `TEMP-SENSOR`; the smoke device's registration or reachability needs repair. Packet Tracer's installed IoT help (`help/default/iot_using_things.htm`) states the default Home Gateway IoE account is `admin` / `admin`; enter it manually in the tablet's browser. The gateway Internet address timed out from PC3's browser; use the local tablet for IoT monitoring.

## Router configuration

On Router0:

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
3. Server0 HTTP is On. Open `http://10.10.30.10` from PC0 to reproduce the verified routed HTTP path and AURA landing page. Its source is [server-index.html](server-index.html); edit it in Server0 > Services > HTTP > `index.html` if rebuilding the topology. PC3 can also open the page locally on the server LAN.
4. In Simulation mode filter ICMP and HTTP. Send periodic simple PDUs from TEMP and SMOKE to MONITOR as routine telemetry; send an immediate PDU from ALERT as the critical-alert scenario. Record packet paths and timestamps as demonstration evidence.
5. Check the Temperature Monitor value and Smoke Detector alarm and level fields in the Home Gateway IoT device page. The verified saved state exposed the fields.
6. To test the car, use **Alt-click** on `SMOKE-TRIGGER-CAR` or set its `state` property to `1` in Attributes. Packet Tracer's Old Car specification requires the car and detector to share a physical container; the saved topology places both in Main Wiring Closet. Observe the detector's `level` and `state` while advancing the environment clock, then turn the car off. On 2026-10-29, the car showed `state 1` but the detector remained at `level 34.18050003051758, state 0` after the clock passed 1:47:30. No car-caused alarm was observed. The saved car state is `0`.

### If the car does not raise the smoke reading

Packet Tracer 9.0's installed **Environment** help says the Old Car raises smoke at **3% per simulated hour in a 100,000 cm³ container**; a larger container weakens its effect. Main Wiring Closet may still be too large, but its volume was not measured and the reason for the absent car-caused alarm is unproven. If adjusting the physical setup, measure the starting Smoke environment value and detector `level/state`, turn the car on, advance the environment clock, and record both values again. Confirm `state 1` in the detector and the gateway Devices page before claiming success. Keep the gateway and tablet associated after any physical move. The installed reference is `help/default/environment.htm` in the Packet Tracer 9.0 installation.

For a separate **detector-threshold check**, the Environment dialog's Advanced Settings includes a *Manual Adjustment* control. On 2026-10-29, setting Smoke in Main Wiring Closet to `100` and advancing the environment clock changed the detector from `level 10.048500061035156, state 0` to `level 69.21540069580078, state 1`; after the adjustment was removed it returned to `level 36.340999603271484, state 0`. The gateway Devices page was not read during this test because its login page required lab credentials. This threshold response does not prove that the Old Car supplied the smoke. Packet Tracer's environment clock is separate from its network simulation clock.

Packet Tracer simple PDUs do not model custom UDP reliability, retransmission deadlines, or the NS2 traffic generator. The NS2 topology mirrors the two-ended routed path at a logical level, with an additional background sender to stress the bottleneck.
