# Cisco Packet Tracer smart-campus demonstration

The saved topology includes an Old Car named `SMOKE-TRIGGER-CAR` beside the native Smoke Detector in Corporate Office → `SMOKE-TEST-CHAMBER`, a 1 m³ physical container. A manual Smoke adjustment triggered the detector in Main Wiring Closet on 2026-10-29. The car's physical **Interact** control subsequently produced a separate detector alarm in the small chamber.

The editable [campus topology](../topology/AURA-UDP-campus.pkt) contains the routed network, traffic-generator PCs, a DLC100 Home Gateway, a Temperature Monitor, and a Smoke Detector. PC0-to-Server0 simple ICMP PDU succeeded after ARP learning. PC1 and PC2 each pinged Server0 successfully, and PC3 pinged PC2 successfully. Sensor-side PC0 loaded the custom [AURA landing page](server-index.html) from Server0 over HTTP through Router0 and Router1 in Packet Tracer 9.0, including after the 2026-10-29 physical move. PC3 also loaded the page, but PC3 and Server0 share the server LAN. Both native sensors appeared on the gateway Devices page after reconnecting `SMOKE-SENSOR` to Home Gateway. Packet Tracer demonstrates connectivity and the campus scenario; it does not execute AURA-UDP.

## Devices and cabling

The saved topology uses two 2911 routers (Router0 and Router1), two 2960 switches (Switch0 and Switch1), one Server-PT (Server0), three PC-PT devices (PC0/1/2, representing temperature, smoke and alert *traffic generators*), one operations PC (PC3), and a wireless tablet (Tablet PC0). The PCs and server connect to switches with copper straight-through cables. Switch0 connects to Router0 Gi0/0, Router0 Gi0/1 connects to Router1 Gi0/0, and Router1 Gi0/1 connects to Switch1. The Home Gateway Internet port connects to Switch0; the native Temperature Monitor, Smoke Detector, and tablet use its wireless network. Cisco's [Packet Tracer IoT activity](https://contenthub.netacad.com/legacy/I2IoT/2.0/en/course/files/1.2.2.1%20Packet%20Tracer%20-%20Adding%20IoT%20Devices%20to%20a%20Smart%20Home.pdf) documents the registration workflow.

## Address plan

| Segment | Network | Router | Hosts |
|---|---|---|---|
| Sensors and alerts | 10.10.10.0/24 | Router0 Gi0/0 10.10.10.1 | PC0 .11, PC1 .12, PC2 .13, HomeGateway0 Internet .2 |
| Transit | 10.10.20.0/30 | Router0 Gi0/1 .1, Router1 Gi0/0 .2 | — |
| Server and operations | 10.10.30.0/24 | Router1 Gi0/1 10.10.30.1 | MONITOR .10, OPS .11 |

Set each host's mask to 255.255.255.0 and default gateway to its local router address.

HomeGateway0 has Internet address `10.10.10.2/24` and gateway `10.10.10.1`. Its internal IoT subnet is `192.168.25.0/24`. The native devices are named TEMP-SENSOR and SMOKE-SENSOR; earlier checks showed wireless association, static internal addresses `192.168.25.11` and `192.168.25.12`, and Home Gateway as their IoT server. Tablet PC0 uses SSID HomeGateway and static address `192.168.25.20` because its DHCP request failed in this saved lab. On 2026-10-29, the refreshed post-move Devices page initially listed only `TEMP-SENSOR`. Toggling `SMOKE-SENSOR`'s IoT Server setting from None back to Home Gateway restored it; the page then showed both devices and smoke Level `34.1754`. Packet Tracer's installed IoT help (`help/default/iot_using_things.htm`) states the default Home Gateway IoE account is `admin` / `admin`; enter it manually in the tablet's browser. The gateway Internet address timed out from PC3's browser; use the local tablet for IoT monitoring.

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
6. In Physical view navigate to Corporate Office → `SMOKE-TEST-CHAMBER`. The car and detector share this 1 m³ chamber. Record the detector's Attributes `level` and `state` with the car off. Right-click `SMOKE-TRIGGER-CAR` and choose **Interact** (or Alt-click it) to start it; visible exhaust confirms physical activation. Advance the Environment clock and refresh the detector's Attributes. In the 2026-10-29 test its reading changed from `level 0.00011444099083227316, state 0` to `level 100, state 1`. Use **Interact** again to stop the car. The saved car state is `0`. Merely editing the car's Attributes `state` to `1` did not reproduce the emission in this test.

### Smoke test interpretation

Packet Tracer 9.0's installed **Environment** help says the Old Car raises smoke at **3% per simulated hour in a 100,000 cm³ container**; a larger container weakens its effect. The car did not cause an observed alarm in Main Wiring Closet, whose volume was not measured. The 1 m³ chamber is the minimum size accepted by Packet Tracer's physical properties dialog. The Environment dialog's Location menu did not list this new chamber, so an independent chamber Smoke value could not be captured. The detector's live level and state supplied the observed car transition. Keep the gateway and tablet associated after any physical move. The installed reference is `help/default/environment.htm` in the Packet Tracer 9.0 installation.

For a separate **detector-threshold check**, the Environment dialog's Advanced Settings includes a *Manual Adjustment* control. On 2026-10-29, setting Smoke in Main Wiring Closet to `100` and advancing the environment clock changed the detector from `level 10.048500061035156, state 0` to `level 69.21540069580078, state 1`; after the adjustment was removed it returned to `level 36.340999603271484, state 0`. The gateway Devices page was unavailable during that test because its login page required manual sign-in. This was a distinct test from the car-caused alarm. Packet Tracer's environment clock is separate from its network simulation clock.

Packet Tracer simple PDUs do not model custom UDP reliability, retransmission deadlines, or the NS2 traffic generator. The NS2 topology mirrors the two-ended routed path at a logical level, with an additional background sender to stress the bottleneck.
