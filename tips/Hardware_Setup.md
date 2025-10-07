# Connecting to the Pi
**Username:** ubuntu

**Password:** cryosphere

Both Raspberry Pi’s are running Ubuntu Server which is a simplified version of Linux that only has a terminal (no GUI). It cannot be used to show graphs or run applications. Since the university Wi-Fi requires signing in through a browser, they have been whitelisted on the UCB Wireless network by the IT department. If you would like to change any details about the Wi-Fi networks or IP addresses, edit /etc/netplan/50-cloudinit-???.yaml 

The Pi’s have both been set up with a clone of the EricGosnell/uhd_radar repository in the ~/uhd_radar folder, and all the necessary dependencies are already installed. The operating system and code are installed on the SD card, but the uhd_radar/data/ folder is mounted on the 4 TB SSD. The baseline branch contains Thomas’ code from when we forked the repo, and main contains our most recent code. The Pi’s are not signed in to any GitHub account, so you cannot push any code to GitHub, though you can still pull any recent changes. See the section below for details on how to send files to and from the Pi. 

There are a couple of ways to access the terminal on Raspberry Pi’s. The first method is to just control it directly, which can be useful for setting up the device or debugging problems with the other methods, but it is more limited and does not work for field testing. The better solution is to connect to the Pi from your laptop over an SSH tunnel, preferably via ethernet though it can be done over Wi-Fi too.  

## Direct Control: 

This method requires a monitor and keyboard, cannot be used to share files between a laptop and the Pi, and is more difficult to use. **I would only recommend this method if it were needed while setting up an SSH connection from your laptop, or you are unable to use the other methods for some reason.**

To access the Pi’s terminal directly you will need: 
1. Raspberry Pi 5 
1. Pi Power Supply (plugged into wall) 
1. Monitor (plugged into wall) 
1. HDMI to Micro-HDMI cable 
1. Keyboard 
1. Ethernet cable connected to a router (or ethernet port on the wall of the lab)

Simply connect the ethernet (or just use WiFi), micro-HDMI, keyboard, and power supply to the Raspberry Pi. When it boots, you will see the Pi’s Ubuntu Server terminal on the monitor and can log in and run commands directly with the keyboard (no mouse inputs). There is no way to scroll up through this terminal however, so if you want to be able to read a long output from a command you must pipe it into a file (ex. python run.py >> terminal_output.txt), then read the text file using nano. 

## Setting up SSH: 

In order to be able to connect to the Pi via SSH, the Pi must have your laptop's public SSH key. If you do not already have an SSH key, you can create one as follows: 

1. In your terminal (PowerShell on Windows) run `ssh-keygen -t ed25519 -C “your@email.com”` and accept the default location.  
1. Create a memorable password. When you type the password, no text will appear in the terminal but the password is being logged.  
1. We now need to copy the public key you just created. When the key was generated, a message should have been printed that says something like Your public key has been saved in /home/<username>/.ssh/id_ed25519.pub.  
1. To view the contents of this public key file, run  `cat <path-from-above>/.ssh/id_ed25519.pub` and copy the full key that is printed to the terminal.

You then need to add this SSH to the Pi. The simplest method is to first add the key to your GitHub account, then import it onto the Pi from there. If you don’t want to set up GitHub, you can add the key directly with a little extra work. 

**GitHub:** 
1. Create an account on GitHub and sign in. 
1. In GitHub, open settings and go to the SSH and GPG keys tab and add a new SSH key. 
1. Name this key whatever you want and paste the key into the correct field. 
1. Log into the Pi using the direct control method above. 
1. Run `ssh-import-id gh:<your-github-username>`.

**Without GitHub:**
1. Log into the Pi using the direct control method above. 
1. Open the authorized keys file with `sudo nano ~/.ssh/authorized_keys`. 
1. Manually copy your key (starts with ssh-ed25519, ends with a comment) into the file 
1. Hit Ctrl+X followed by Y, then Enter to save the changes. 

You should now have permission to SSH into the Pi from your laptop using one of the following methods. 

## SSH over Ethernet: 

**This is the preferred method for connecting to and controlling the Pi**, and the only method that does not require the Pi to be connected to a router or Wi-Fi network. However, it does take a bit of setup the first time. 

For this method, you will need: 
1. Laptop connected to Wi-Fi 
1. Raspberry Pi 5 
1. Pi Power Supply (plugged into wall) 
1. Ethernet cable 
1. Ethernet to usb-c adapter (if your laptop doesn’t have an ethernet port) 

**Process**
1. Plug the power supply into the Pi and plug one end of the ethernet cable into the Pi, and the other into your laptop. 
1. Connect your laptop to any Wi-Fi network. 
1. If your laptop's public SSH key is not already on the Pi, see the section above for how to add it. 
1. If this is your first time setting up this method, you will now need to enable internet sharing on your laptop. If you have done this before, then skip this step.
   
     **Windows:**
      1. Open Control Panel and go to the Network section. 
      2. Find the Wi-Fi connection and right click on it, then go to Properties. 
      3. At the top, click on the Sharing tab. 
      4. Check “Allow other network users to connect...” 
      5. In the dropdown, select “Ethernet2” (not the ethernet for WSL). 
      6. Apply the changes.
         
     **Linux:** 
      1. Install Network Manager Command-line Interface (nmcli) with `sudo apt install network-manager`. 
      2. Find the connection name with `nmcli con show`. Find the entry with type ethernet, it should have a name like “Wired connection 1”. 
      3. Run `nmcli con modify “Wired connection 1” ipv4.method shared`. 
1. If you are on Linux, run ‘nmcli con up “Wired connection 1”’ 
1. Find the Pi’s IP address on your local subnet. 
    1. If you are on Windows, open PowerShell and run `arp -a`. You should see an interface for 192.168.137.1 and within that section should be an IP address that starts with 192.168.137 and ends with something other than .0   or .1 (ex. 192.168.137.27).  
    2. If you are on Linux, then Pi #1 always has the IP 10.42.0.10, and Pi #2 always has the IP 10.42.0.20. If for some reason you cannot find the IP, confirm the subnet is 10.42.0 by running `ip a`. Under the enxc...   section should say “state UP” and you should see “inet 10.42.0.1/24”. You can then scan the subnet to find the pi by running `nmap -sn 10.42.0.1/24` and looking for a device that’s not 10.42.0.1. You may need to restart   the Pi and give it a minute to boot. 

1. Run `ssh ubuntu@<pi-ip-address>` to connect to the Pi. You can now run commands on the Pi, and transfer files to and from your laptop using SCP (see above).

## SSH over Wi-Fi: 

This method is nice as it requires less cables and can be used for connecting multiple devices, **however you will have to use one of the other methods such as SSH over Ethernet initially to find the Pi’s internet IP address.** 

For this method, you will need: 
* Laptop connected to Wi-Fi 
* Raspberry Pi 5 
* Pi Power Supply (plugged into wall) 
* Ethernet cable connected to a router (or to the ethernet port on the wall of the lab) if not connecting the Pi to Wi-Fi

**Process**
1. Plug the ethernet and power cable into the Pi and turn it on.
1. If you do not know what the Pi’s current IP address is, you must first use the Direct Control method above to get access to the terminal. When the Pi first boots, system information is printed to the terminal. In the bottom right corner of this message, you should see a section that says “IPv4 address for eth0: 128.138.189.xxx”. You can also find the IP address by running `ip a` and looking for the address under the eth0 section. This address may change each time the Pi is reconnected to the internet. 
1. Connect your laptop to the UCB Wireless network. 
1. Check if you can find the Pi over the internet by running the command `ping -c 1 128.138.189.xxx` (where xxx is replaced by the Pi’s IP). On Windows, this must be done in PowerShell, not WSL. If it says 0 packets received, then either the IP address is incorrect, or you are not on the same network as the Pi. 
1. If your laptop's public SSH key is not already on the Pi, see the section above for how to add it. 
1. Run `ssh ubuntu@128.138.189.xxx` to connect to the Pi. You can now run commands on the Pi, and transfer files to and from your laptop using SCP (see above).

## Transferring files to and from the Pi: 

The Raspberry Pi 5 unfortunately does not support data transfer (USB OTG) over its USB 3.0 ports, only the USB C port which we currently use for power. Fortunately, we can make use of the SSH connection to send files to and from the Pi using SCP and/or GitHub. 

If you have committed changes to the code and pushed them to GitHub, you can just checkout the correct branch and run `git pull` on the Pi to see them. However, if you are debugging or making small changes to a file that aren’t worthy of a commit, you can send files directly with SCP by running the following command on your laptop. 

Send a single file with `scp <my-file-path> ubuntu@<pi-ip-address>:<pi-directory-path>`. 
* Windows: `scp sdr\main.cpp ubuntu@192.168.137.10:~/uhd_radar/sdr/`
* Linux: `scp sdr/main.cpp ubuntu@10.42.0.10:~/uhd_radar/sdr/`

You can also send a whole folder with `scp -r <my-directory-path> ubuntu@<pi-ip-address>:<pi-directory-path>`. 

To send files from the Pi back to your laptop, reverse the two arguments ensuring the first is one or more files, or directory, and the second is a directory for where the file should go.  

ex. `scp ubuntu@10.42.0.10:~/uhd_radar/data/20250716* ~/uhd_radar/data/`. 

# Indoor Testing: 

While indoors, make sure **not** to transmit any signals with the antenna. Only transmit into the spectrum analyzer or in a loopback configuration to the SDR. 

**Before doing any testing in a loopback configuration, use the spectrum analyzer to confirm that the transmitted power is less than the maximum input power the SDR can handle.** 

When connecting any SMA cable, make sure to hold the cable and connection point still while you connect it so that the cable **does not spin** as you tighten the nut, as this can cause damage to the pin. Tighten the nut using the SMA torque wrench (the wrench will bend when the proper tightness is reached). 

## 
