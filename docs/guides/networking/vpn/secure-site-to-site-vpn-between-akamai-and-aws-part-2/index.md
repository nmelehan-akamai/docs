---
slug: secure-site-to-site-vpn-between-akamai-and-aws-part-2
title: "Secure Site to Site Vpn Between Akamai and Aws Part 2"
description: "Two to three sentences describing your guide."
og_description: "Optional two to three sentences describing your guide when shared on social media. If omitted, the `description` parameter is used within social links."
authors: ["Linode"]
contributors: ["Linode"]
published: 2025-07-16
keywords: ['list','of','keywords','and key phrases']
license: '[CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0)'
external_resources:
- '[Link Title 1](http://www.example.com)'
- '[Link Title 2](http://www.example.net)'
---


**🔧 Implementation Guide**

1. **Create a Site-to-Site VPN Connection in AWS**

   1. Please follow the official AWS documentation linked below to create a Site-to-Site VPN using the AWS Console:
      👉 [**Create a Site-to-Site VPN Connection \- AWS Documentation**](https://docs.aws.amazon.com/vpn/latest/s2svpn/SetUpVPNConnections.html)
      Once the VPN connection is created successfully, follow the steps below to download the StrongSwan configuration.

   2. **download the StrongSwan configuration**

   **📥 How to Download StrongSwan Configuration from AWS**

1. Go to the **VPC Dashboard** in the AWS Console.
2. Navigate to **Site-to-Site VPN Connections**.
3. Select the VPN connection you just created.
4. Click on the **Actions** dropdown and choose **Download Configuration**.
5. In the dialog:
   * **Vendor**: Select **StrongSwan** (or **Generic** if StrongSwan is not listed).
   * **Platform**: Choose **StrongSwan** or leave as default.
   * **Software**: Select **StrongSwan**.
6. Click **Download**.

   This configuration file will contain:

* Tunnel1 and Tunnel2 outside IPs
* Inside tunnel IP addresses
* Pre-shared keys (PSK)
* StrongSwan-compatible configuration snippets

---

2. **Install and configure a StrongSwan VPN Server on Linode**

We use a Linode instance with two NICs:

* use **Ubuntu 24.04 LTS**
* Linode instance has **two NICs**:
  * eth0: for internal VPC communication (e.g., 192.168.1.3)
  * eth1: for encrypted VPN traffic (e.g., 172.16.0.1)

---

**🧱 Step 1: Install StrongSwan**

sudo apt update
sudo apt install \-y strongswan net-tools iptables-persistent

---

**🗂️ Step 2: Configure /etc/ipsec.conf**

To configure the IPSec VPN, update the configuration file:
sudo vim /etc/ipsec.conf

**🔗  View Full Configuration on GitHub**
For the complete ipsec.conf configuration, visit the [\[ipsec.conf\]](https://github.com/sandipgangdhar/linode-aws-vpn-setup/blob/387cf1440989c4014ef6c59969450608f0e63a3d/ipsec.conf)
**🛠️ Note:** Before copying this configuration to your server, **replace the placeholder values** (marked in \<angle brackets\>) with your actual environment details:

####

#### *🔍 Where to Find These Values:*

* **StrongSwan Configuration File:**
  Downloaded earlier from the **AWS VPN Console** when setting up the VPN.
* **AWS VPN Console:**
  If you are unable to locate any of these values, visit the **AWS VPN Console** → **Site-to-Site VPN Connections** → **Tunnel Details**.

**🔄 Example Value Mapping**

| Placeholder | Example Value | Description |
| :---: | :---: | :---: |
| \<Linode VPN Server Public IP\> | 172.236.190.202 | The public IP of your Linode VPN server. |
| \<AWS Tunnel1 Outside IP\> | 3.6.159.10 | The outside IP for AWS Tunnel 1\. |
| \<AWS Tunnel2 Outside IP\> | 13.126.21.208 | The outside IP for AWS Tunnel 2\. |
| \<Linode VLAN Network\> | 172.16.0.0/12 | The private VLAN network in Linode. |
| \<AWS VPC Network\> | 10.0.0.0/16 | The private VPC network in AWS. |
| \<AWS VPC Network CIDR\> | 10.0.0.0/16 | The CIDR block for AWS VPC. |
| \<Local tunnel address\> | 169.254.211.190/30 | Local Tunnel interface IP Address |
| \<Remote tunnel address\> | 169.254.211.189/30 | remote Tunnel interface IP Address |
| \<Tunnel mark\> | 0x64 | Tunnel Mark |
| \<Tunnel mark\> | 0xC8 | Tunnel Mark |
| \<Local tunnel address\> | 169.254.91.58/30 | Local Tunnel interface IP Address |
| \<Remote tunnel address\> | 169.254.91.57/30 | remote Tunnel interface IP Address |

---

**🔐 Step 3: Configure /etc/ipsec.secrets**

sudo vim /etc/ipsec.secrets

**🛠️ Note:** Before copying this to your server, **replace the placeholder values** (inside \<angle brackets\>) with your actual public IPs and pre-shared keys from your AWS VPN configuration.

For sample ipsec.secrets visit the [\[ipsec.secrets\]](https://github.com/sandipgangdhar/linode-aws-vpn-setup/blob/ed2a2798451af86faaf3c4891b001723fbd55680/ipsec.secrets)
Replace the content with:
\<Linode VPN Server Public IP\> \<AWS Tunnel1 Outside IP\> : PSK "\<Tunnel1 Pre-Shared Key\>"

\<Linode VPN Server Public IP\> \<AWS Tunnel2 Outside IP\> : PSK "\<Tunnel2 Pre-Shared Key\>"

**🔄 Example Value Mapping**

| Placeholder | Example Value |
| :---: | :---: |
| \<Linode VPN Server Public IP\> | 172.236.190.202 |
| \<AWS Tunnel1 Outside IP\> | 3.6.159.10 |
| \<AWS Tunnel2 Outside IP\> | 13.126.21.208 |
| \<Tunnel1 Pre-Shared Key\> | eSZ0FSFSFASfbqxn8DMXcMLAlIFH8b |
| \<Tunnel2 Pre-Shared Key\> | Sz80tgkqxTDy0q.EDFSDE57uSt5\_ |

---

**🔐 Step 4: Configure /usr/local/bin/vpn-updown.sh **

The vpn-updown.sh script is a custom **leftupdown handler** for **StrongSwan**. It is triggered automatically whenever an IPsec tunnel is brought **up** or **down**. The script handles critical networking tasks to establish proper routing, firewall rules, and interface configuration for seamless VPN connectivity.
**🔗  View Full script on GitHub**
For the complete vpn-updown.sh script, visit the [\[vpn-updown.sh\]](https://github.com/sandipgangdhar/linode-aws-vpn-setup/blob/ed2a2798451af86faaf3c4891b001723fbd55680/vpn-updown.sh)
**🛠️ Note:** Before copying this script to your server, **replace the placeholder values** (marked in \<angle brackets\>) with your actual environment details:

**🔄 Argument Parsing**

Accepts the following parameters:

| Flag | Description |
| :---: | :---: |
| \-ln / \--link-name | Name of the virtual tunnel interface (e.g., Tunnel1) |
| \-ll / \--link-local | Local IP address of the tunnel interface |
| \-lr / \--link-remote | Remote (AWS-side) tunnel IP address |
| \-m / \--mark | Hex or decimal mark used for routing and iptables tagging |
| "-l|--local-route" | Linode VLAN network |
| "=--static-route" | Comma-separated list of static route CIDRs (usually AWS subnets) |

**🔧 What Happens on Tunnel Up (up-client)**

When the IPsec tunnel is established and the up-client event triggers, the following steps are executed in sequence:
✅ **Step 1:** **VTI Interface Creation**

* A **Virtual Tunnel Interface (VTI)** is created using ip link add, representing the VPN tunnel.
* This interface allows direct IP routing through the VPN without IPsec encapsulation issues.

✅ **Step 2: IP Address Assignment**

* The **Local IP** and **Remote IP** are assigned to the VTI interface.
* These are the internal IP addresses for the tunnel endpoints.

✅ **Step 3:** **Sysctl Configuration**

* Enables IP forwarding to allow packet routing.
* Disables **policy transformation** on the interface (disable\_policy) to avoid conflicts with StrongSwan.
* Disables **XFRM (IPsec transformation)** on the VTI to prevent double encryption.

✅ **Step 4:** **Routing Table Setup**

* Ensures that the custom routing table (customvpn) exists in /etc/iproute2/rt\_tables.
* If not present, the script dynamically creates it.

✅ **Step 5:** **Static Route Addition**

* Routes are added to the AWS subnet(s) using the VTI interface.
* This allows packets destined for AWS to flow correctly through the VPN.

✅ **Step 6:** **IP Rule Association**

* A specific ip rule is added to associate traffic marked with the tunnel’s unique mark (0x64 for Tunnel1, 0xc8 for Tunnel2) with the customvpn routing table.
* This is crucial for directing packets through the correct VTI interface.

✅ **Step 7:** **IPTables Configuration (Mangle & NAT Rules)**

* **Filter Table**

The filter table manages basic packet filtering for traffic flowing through the VPN tunnel interfaces: Accepts traffic flowing through Tunnel1 and Tunnel2 and Prevents firewall restrictions on these interfaces

* **NAT Table POSTROUTING Rules (RETURN)**

This ensures that traffic destined for AWS subnets does not undergo NAT if it matches the specified subnets.

* **NAT Table POSTROUTING Rules (MASQUERADE)**

When packets are forwarded out through eth0, the source IP is rewritten to the public IP of the Linode instance.

* **NAT Table POSTROUTING SNAT Rule for Tunnel**

     This handles the source address translation for packets traveling through the tunnel. It rewrites the source IP to match the VPN server’s IP which ensures that AWS sees the traffic as coming from the Linode VPN server, facilitating proper routing back through the tunnel.

* **Mangle Table PREROUTING Rules**

These rules mark incoming traffic with the appropriate fwmark. This mark is used to route traffic through the correct VPN tunnel in the custom routing table.

* **Mangle Table OUTPUT Rules**

This ensures that outgoing traffic from the VPN server itself is marked properly. This is especially important for direct pings or direct connections initiated from the VPN server.

### 🔻 **What Happens on Tunnel Down (down-client)**

When the IPsec tunnel is brought down, the following steps are performed gracefully:
🛑 **Step 1:** Route and Rule Cleanup

* All custom routing rules associated with the VTI are removed.
* Prevents stale routes that could cause traffic blackholes.

🛑 **Step 2:** IPTables Cleanup

* Removes all firewall marks and NAT rules related to the tunnel.
* Ensures there are no lingering rules that could affect traffic flow.

🛑 **Step 3:** VTI Interface Removal

* The VTI interface is brought down and deleted gracefully.
* This prevents conflicts during the next tunnel establishment.

**🛠️ Note:** Before copying this to your server, **replace the placeholder values** (inside \<angle brackets\>) with your actual public IPs and pre-shared keys from your AWS VPN configuration.

For sample ipsec.secrets visit the [\[vpn-updown.sh\]](https://github.com/sandipgangdhar/linode-aws-vpn-setup/blob/ed2a2798451af86faaf3c4891b001723fbd55680/vpn-updown.sh)

sudo vim /usr/local/bin/vpn-updown.sh

**🛠️ Note:**Before using, replace all values inside \<angle brackets\> with actual data based on your environment.

**🔄 Example Value Mapping**

| Placeholder | Description | Example Value |
| :---: | :---: | :---: |
| \<LOG\_FILE\> | Log file location where all the VPN-related logs are stored. | /var/log/vpn-updown.log |
| \<DEBUG\_MODE\> | Mode to enable or disable debug logging. 1 enables debug mode; 0 disables it. | 1 or 0 |
| \<INTERFACE\> | The main network interface for outgoing traffic. Typically used for NAT. | eth0 |
| \<ROUTE\_TABLE\_NAME\> | Name of the custom routing table used for the VPN traffic. | customvpn |
| \<LAST\_SWITCH\_FILE\> | File that records the last active tunnel and its timestamp. | /var/run/vpn\_last\_switch |
| \<LOCK\_FILE\> | Lock file used to prevent race conditions during updates. | /var/run/vpn\_switch.lock |

### ✅ **How to Enable and Use**

sudo chmod 744 /etc/ipsec.d/aws-updown.sh

### 💡 Key Points to Note:

* The script is tightly integrated with **StrongSwan’s up-down event triggers**, ensuring that all networking changes happen at the right time.
* It is designed to be idempotent, meaning if the configurations already exist, it simply logs and skips re-configuration.
* iptables  rules are carefully crafted to prevent duplicate entries and ensure proper routing.

---

**🔐 Step 5: Configure /usr/local/bin/vpn-failover.sh**

The vpn-failover.sh script is a custom failover monitoring solution designed to automatically switch VPN tunnels between **Tunnel1** and **Tunnel2** in the event of a failure. This script continuously monitors both VPN tunnels and dynamically adjusts routes, IP rules, and iptables configurations to ensure uninterrupted connectivity.
**🔗  View Full script on GitHub**
For the complete vpn-failover.sh script, visit the [\[vpn-failover.sh\]](https://github.com/sandipgangdhar/linode-aws-vpn-setup/blob/ed2a2798451af86faaf3c4891b001723fbd55680/vpn-failover.sh)
**🛠️ Note:** Before copying this script to your server, **replace the placeholder values** (marked in \<angle brackets\>) with your actual environment details:

### 🔄 How It Works

The script runs in a continuous loop (by default, every 60 seconds) to:

1. **Check Tunnel Status:**
   * Pings the AWS private IP through each tunnel.
   * Determines if the tunnel is **UP** or **DOWN**.
2. **Failover Logic:**
   * If the primary tunnel (Tunnel1) is **DOWN**, the script automatically switches traffic to the secondary tunnel (Tunnel2) and vice versa.
   * Routes, IP rules, and iptables are dynamically adjusted to reflect the active tunnel.
3. **Logging and State Tracking:**
   * Logs all activities to /var/log/vpn-failover.log.
   * Tracks the last active tunnel and its timestamp in /var/run/vpn\_last\_switch.

### ✅ What Happens During Tunnel Monitoring

When the script detects a tunnel as **active**, it performs the following steps in sequence:

### ✅ Step 1: Verify Tunnel Status

• The script first checks the /var/run/vpn\_last\_switch file to determine if the tunnel is already up or still initializing.
• If the tunnel is initializing, it waits for the grace period (120 seconds) before attempting to ping.
• This prevents premature failover during tunnel boot-up.

### ✅ Step 2: Ping Tests and Failover Detection

• ICMP ping is sent to a known AWS private IP through both tunnels (Tunnel1 and Tunnel2).
• If the primary tunnel (Tunnel1) fails to respond, it switches to the secondary tunnel (Tunnel2).
• All routes and IP rules are reconfigured dynamically.

### ✅ Step 3: Dynamic Routing Configuration

When a failover occurs:
• Routes in the custom routing table customvpn are adjusted to reflect the new active tunnel.
• Example:
ip route add 10.0.0.0/16 via 169.254.91.58 dev Tunnel1 table customvpn metric 100
ip route add 10.0.0.0/16 via 169.254.211.190 dev Tunnel2 table customvpn metric 200

• The old route is deleted to prevent asymmetric routing issues.

### ✅ Step4: IP Rule Management

• Custom IP rules are added to associate traffic marked with the tunnel’s fwmark with the custom routing table (customvpn).

• Example:

ip rule add from 172.16.0.0/12 fwmark 0x64 lookup customvpn priority 100
ip rule add from 172.16.0.0/12 fwmark 0xc8 lookup customvpn priority 100

• When switching tunnels, the script dynamically removes old rules and creates new ones.

### ✅ Step5: Static IPTables Rules

• Ensures that static iptables rules are always present.

• Examples include:

* iptables \-t filter \-A FORWARD \-o Tunnel1 \-j ACCEPT
* iptables \-t filter \-A FORWARD \-o Tunnel2 \-j ACCEPT
* NAT masquerading for outgoing traffic through eth0.

### ✅ Step 6: Dynamic Mangle Table Rules

• The script dynamically adjusts mangle table PREROUTING and OUTPUT chain rules based on the active tunnel.
• Ensures that packets are marked with the correct fwmark for routing.
• Example:
iptables \-t mangle \-A PREROUTING \-s 172.16.0.0/12 \-d 10.0.0.0/16 \-j MARK \--set-mark 0x64
iptables \-t mangle \-A OUTPUT \-s 172.16.0.0/12 \-d 10.0.0.0/16 \-j MARK \--set-mark 0x64

### ✅ Step7: Health Check and Service Down Detection

• If the script detects the IPsec service is stopped, it updates the /var/run/vpn\_last\_switch with SERVICE\_DOWN and stops failover attempts.

• Logs the event for easy debugging.

• When the service comes back up, it automatically resumes monitoring.

**🔄 Example Value Mapping**

| laceholder | Description | Example Value |
| :---: | :---: | :---: |
| \<LOG\_FILE\> | Log file location where all the VPN-related logs are stored. | /var/log/vpn-failover.log |
| \<DEBUG\_MODE\> | Mode to enable or disable debug logging. 1 enables debug mode; 0 disables it. | 1 or 0 |
| \<LAST\_SWITCH\_FILE\> | File that records the last active tunnel and its timestamp. | /var/run/vpn\_last\_switch |
| \<LOCK\_FILE\> | Lock file used to prevent race conditions during updates. | /var/run/vpn\_switch.lock |
| \<PING\_IP\> | The AWS private IP used for ping health checks. | 10.0.4.85 |
| \<ROUTE\_TABLE\_NAME\> | Name of the custom routing table used for the VPN traffic. | customvpn |
| \<PRIMARY\_TUNNEL\> | Name of the primary tunnel interface. | Tunnel1 |
| \<SECONDARY\_TUNNEL\> | Name of the secondary tunnel interface. | Tunnel2 |
| \<MARK\_PRIMARY\> | Fwmark used for the primary tunnel. | 0x64 |
| \<MARK\_SECONDARY\> | Fwmark used for the secondary tunnel. | 0xc8 |
| \<PRIMARY\_IP\> | Local IP address of the primary tunnel interface (VTI interface). | 169.254.91.58 |
| \<SECONDARY\_IP\> | Local IP address of the secondary tunnel interface (VTI interface). | 169.254.211.190 |
| \<SUBNET\_LOCAL\> | The local VLAN subnet for the Linode VPC. | 172.16.0.0/12 |
| \<SUBNET\_REMOTE\> | The AWS VPC subnet where the VPN tunnel terminates. | 10.0.0.0/16 |
| \<VPN\_SERVER\_IP\> | The Linode VPN server’s private IP address. | 172.16.0.2 |
| \<SLEEP\_TIME\> | Time (in seconds) to wait before rechecking tunnel status during initialization. | 5 |
| \<POLL\_INTERVAL\> | Time (in seconds) for how frequently the script checks tunnel status. | 60 |

### 💡 Key Points to Note:

• Script runs in a loop with a configurable interval (POLL\_INTERVAL).

• It is designed to be idempotent, ensuring routes and rules are only added if they are missing.

• Automatically handles failover and failback, with no manual intervention required.

• Logs are stored in /var/log/vpn-failover.log for easy debugging and troubleshooting.

• It is tightly integrated with vpn-updown.sh to ensure smooth handover during IPsec tunnel events.

### ✅  Configure Systemd Service for vpn-failover.sh

To ensure that vpn-failover.sh runs automatically at boot and continuously monitors tunnel status, we configure it as a **systemd service**. This enables the service to start at boot time, automatically restart if it fails, and integrate with system logs for easier debugging.

### 📝 Systemd Unit File Location

The Systemd unit file should be placed at the following location:
/etc/systemd/system/vpn-failover.service

**🔗  View Full systemd Configuration on GitHub**
For the complete vpn-failover.servcice configuration, visit the [\[vpn-failover.service\]](https://github.com/sandipgangdhar/linode-aws-vpn-setup/blob/b174b5808bf1eba7c5396dbcd4361e22e5ae5f75/vpn-failover.service)

🚀 Commands to Enable and Start the Service

\# Enable the service to start at boot
sudo systemctl enable vpn-failover.service

\# Start the service
sudo systemctl start vpn-failover.service

\# Check the status of the service
sudo systemctl status vpn-failover.service

🔍 Checking Logs for Troubleshooting

To monitor the logs generated by the service, use:

sudo journalctl \-u vpn-failover.service \-f

You can also filter logs using the identifier:
sudo grep "vpn-failover" /var/log/syslog

🛡️ Benefits of Using Systemd:

1. **Automatic Start:** Ensures the VPN monitoring script starts with the OS.
2. **Auto-Restart:** If the script crashes, it will automatically restart after 10 seconds.
3. **Unified Logging:** Logs are consolidated in journalctl and /var/log/syslog.
4. **Dependency Management:** Only starts after IPsec service and network are ready.

---

### 🚀 Starting IPsec and Verifying Tunnel Status

Now that everything is configured, follow the steps below to start StrongSwan and validate that both VPN tunnels are operational.

#### *✅ Step 1: Start the StrongSwan IPsec Service*

Run the following command to start IPsec:
sudo systemctl start ipsec

Ensure the service is running:
sudo systemctl status ipsec

To automatically start on boot:
sudo systemctl enable ipsec

#### *✅ Step 2: Start the vpn-failover Service*

To Enable the vpn-failover service to start at boot

sudo systemctl enable vpn-failover.service

To start the vpn-failover service

sudo systemctl start vpn-failover.service

To Check the status of the

service  sudo systemctl status vpn-failover.service

---

**🔎🔎 Testing and Validation**

Once the IPsec VPN, failover script, and systemd service are configured, it’s crucial to thoroughly test and validate the setup to ensure reliability and performance. Below are the structured testing steps:

**✅** *Step 1: Check The Tunnel Status in AWS Console*

1. Go to the **VPC Dashboard \> Site-to-Site VPN Connections**
2. Select your VPN connection
3. Scroll down to **Tunnel Details**
4. Confirm that **Tunnel 1** and **Tunnel 2** both show:
   * **Status**: UP
   * **Phase 1 & Phase 2 Negotiation**: Success
   * **Last Status** *Change*: Reflects recent activity

**✅** *Step 2:Verify the Tunnel Interfaces*

Check if both tunnel interfaces are created and are in the **UP** state:

ip link show Tunnel1
ip link show Tunnel2

You should see:

* Tunnel1 and Tunnel2 listed with **state UP**.
* Local IP: 169.254.91.58 for Tunnel1 and 169.254.211.190 for Tunnel2.
* Remote IP: 169.254.91.57 for Tunnel1 and 169.254.211.189 for Tunnel2.

### **✅** *Step 3:Validate Routing Table (customvpn)*

Check the custom routing table entries for traffic routing:
ip route show table customvpn

You should see entries like:
10.0.0.0/16 via 169.254.91.57 dev Tunnel1 metric 100
10.0.0.0/16 via 169.254.211.189 dev Tunnel2 metric 200

If the routes are not present, add them manually:
sudo ip route add 10.0.0.0/16 via 169.254.91.57 dev Tunnel1 table customvpn metric 100
sudo ip route add 10.0.0.0/16 via 169.254.211.189 dev Tunnel2 table customvpn metric 200

**✅** *Step 4: Check IP Rules*

Validate that IP rules are set correctly:
ip rule show

Expected output:
100:    from 172.16.0.0/12 fwmark 0x64 lookup customvpn
100:    from 172.16.0.0/12 fwmark 0xc8 lookup customvpn

If not found, add them manually:
sudo ip rule add from 172.16.0.0/12 fwmark 0x64 lookup customvpn priority 100
sudo ip rule add from 172.16.0.0/12 fwmark 0xc8 lookup customvpn priority 100

**✅** *Step 5:  Verify NAT Rules (POSTROUTING)*

Check that the NAT rules are applied correctly:
sudo iptables \-t nat \-L \-v \-n

You should see:
RETURN     all  \--  172.16.0.0/12        10.0.0.0/16
MASQUERADE all  \--  172.16.0.0/12        0.0.0.0/0

If missing, add them:
sudo iptables \-t nat \-A POSTROUTING \-s 172.16.0.0/12 \-d 10.0.0.0/16 \-j RETURN
sudo iptables \-t nat \-A POSTROUTING \-s 172.16.0.0/12 \-o eth0 \-j MASQUERADE

**✅** *Step 6:  Verify Mangle Rules*

Ensure the Mangle rules are applied correctly:
sudo iptables \-t mangle \-L \-v \-n

You should see:
\* FORWARD \-s 172.16.0.0/12 \-d 10.0.0.0/16 \-o Tunnel1 ...
\* FORWARD \-s 172.16.0.0/12 \-d 10.0.0.0/16 \-o Tunnel2 ...
\* OUTPUT  \-s 172.16.0.0/12 \-d 10.0.0.0/16 \-o Tunnel1 MARK set 0x64
\* OUTPUT  \-s 172.16.0.0/12 \-d 10.0.0.0/16 \-o Tunnel2 MARK set 0xc8

If missing, re-run the **vpn-updown.sh** script.

### **✅** *Step 7:   Verify XFRM Policies*

Check if XFRM (IPsec policies) are correctly applied:
ip xfrm policy

You should see:

* src 172.16.0.0/12 to 10.0.0.0/16
* dst 10.0.0.0/16 to 172.16.0.0/12

### **✅** *Step 8: Perform Ping Tests*

\# Ping an AWS instance from the Linode VLAN:
ping \-I 172.16.0.1 10.0.4.85
ping \-I 172.16.0.2 10.0.4.85

If it still fails:
\# Monitor traffic flow:
sudo tcpdump \-i Tunnel1 icmp or esp
sudo tcpdump \-i Tunnel2 icmp or esp
sudo tcpdump \-i eth0 icmp or esp

**✅** *Step 8: Check IPsec Logs*

To troubleshoot deeper:
sudo tail \-f /var/log/syslog | grep charon

Look for:

* NO\_PROPOSAL\_CHOSEN
* AUTHENTICATION\_FAILED
* CHILD\_SA not established
* IKE\_SA deleted

### **✅** *Step 9:* Verify IP Forwarding

Ensure IP forwarding is enabled:
sysctl net.ipv4.ip\_forward

If it returns 0, enable it:
sudo sysctl \-w net.ipv4.ip\_forward=1

### **✅** *Step 10:* Verify Security Association (SA)

Check the Security Associations (SA):
ip xfrm state

Look for:

* SPI (Security Parameter Index) entries
* Both inbound and outbound are listed.

✅**At this point, your dual-tunnel AWS–Linode VPN setup is fully active.** You now have automatic tunnel healing, failover logic, and secure communication over private IP space.

---

**🌟 Use Cases**

This architecture is ideal for:

* **Hybrid application deployments**

  (e.g., frontend on Linode, backend on AWS)

* **Multi-cloud disaster recovery**

  (mirror workloads or databases across providers)

* **Secure cross-cloud communication**

  (sensitive data exchange between isolated subnets)

---

**✅ Key Benefits**

* **Secure communication** via IPsec encryption
* **Simple integration** with existing VPCs and subnets
* **Scalable design** using dual NICs and VLAN isolation
* **Cost-effective** hybrid cloud connectivity

---

**📌 Conclusion**

With just a few configuration steps and open-source tools like **StrongSwan**, you can build a robust and secure site-to-site VPN between **AWS and Linode**. This enables more flexible and scalable architectures that leverage the strengths of multiple cloud providers.

Whether you’re a cloud architect or DevOps engineer, setting up a site-to-site VPN between Linode and AWS using StrongSwan is a foundational skill that unlocks **multi-cloud flexibility without compromising on control**.

---

**💡 Final Thoughts**

By following the steps outlined above and using the architecture diagram as a reference, you can build a secure and efficient site-to-site VPN setup between AWS and Linode. This not only strengthens your network architecture but also provides a foundation for scalable, hybrid cloud deployments.

If you’re a developer looking to enhance your cloud security and expand your infrastructure, you can apply for up to **$5,000 in Linode credits** to get started:

👉 [Apply for Linode Credits](https://www.linode.com/#request-credits)
---

### 👨‍💻 About the Author

**Sandip Gangdhar** is a **Senior Technical Solutions Architect at Akamai Technologies**, specializing in cloud architecture, network design, and infrastructure modernization. With over a decade of experience in designing and deploying scalable, secure, and resilient systems, he partners with enterprise customers to align technology strategy with business goals.

At Akamai, Sandip leads architectural engagements focused on hybrid cloud, Kubernetes, networking, and security. His core mission is to drive impactful digital transformation through pragmatic, future-ready solutions.

When not architecting infrastructure, Sandip enjoys spending time with his family and exploring advancements in distributed systems and cloud-native technologies.