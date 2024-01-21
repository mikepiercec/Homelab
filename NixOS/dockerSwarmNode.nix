
# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running `nixos-help`).

{ config, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  # Use the systemd-boot EFI boot loader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "canopus"; # Define your hostname.
  # Pick only one of the below networking options.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.
  networking.networkmanager.enable = true;  # Easiest to use and most distros use this by default.

  # Set your time zone.
  time.timeZone = "America/New_York";

  # Set static IP addresses
  networking = {
    interfaces = {
      enp6s18.ipv4.addresses = [{
        address = "192.168.211.226";
        prefixLength = 24;
      }];
      # enp6s19.ipv4.addresses = [{
        # address = "192.168.211.226";
        # prefixLength = 24;
      # }];
    };
    defaultGateway = "192.168.211.1";
  };

  # Set DNS
  networking.nameservers = [ "192.168.211.185" "9.9.9.9" ];

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Add SSH keys
  # users.users."xmike".openssh.authorizedKeys.keys = [
    # "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDarv2qVBRqfSRgzKOdETc18DV5ba5mAQpPxKjWtk88BHdlcVGC2tLi/C8w6q8s3l90VtPCTW3U2tWtelyXJvO8YHkdmpF4NlOKai3x5r0Wzz4j6mCjZPTkRkbINrGq6gEdds+BJM6Mv3Qs08cO/iLJXN9RJFgt42SHriln741qefaYhol2x6hFVuia0/wPZndmb1qOPb9EOQnQ+n4te4QKbWTygtvw4O0Ph/RWxgWK1CXeFHrezYfsLnxzs5HQLIn9kFfcV6ajSENLGhJx/Z1nHTeoedF1piQDz/0PATlUVEgMD2gaQWr+HU2jIFcyG2U4HMYG2gQH17xIdp6fNXyN root@milkyway"
    # "ssh-rsa AAAAB3Nz....6OWM= user" # content of authorized_keys file
    # note: ssh-copy-id will add user@your-machine after the public key
    # but we can remove the "@your-machine" part
  # ];

  # Mount file systems
  fileSystems."/mnt/B_Drive" = {
  device = "192.168.211.174:/volume1/B_Drive"; # NFS server and exported path
  fsType = "nfs"; # Filesystem type
  options = [ "defaults" ]; # Mount options
  };

  fileSystems."/mnt/D_Drive" = {
  device = "192.168.211.174:/volume1/D_Drive"; # NFS server and exported path
  fsType = "nfs"; # Filesystem type
  options = [ "defaults" ]; # Mount options
  # options = [ "rw" "insecure" "sync" "no_subtree_check" "no_root_squash" ];
  };

  fileSystems."/mnt/I_Drive" = {
  device = "192.168.211.174:/volume1/I_Drive"; # NFS server and exported path
  fsType = "nfs"; # Filesystem type
  options = [ "defaults" ]; # Mount options
  };

  fileSystems."/mnt/S_Drive" = {
  device = "192.168.211.174:/volume1/S_Drive"; # NFS server and exported path
  fsType = "nfs"; # Filesystem type
  options = [ "defaults" ]; # Mount options
  };

  fileSystems."/mnt/T_Drive" = {
  device = "192.168.211.174:/volume1/T_Drive"; # NFS server and exported path
  fsType = "nfs"; # Filesystem type
  options = [ "defaults" ]; # Mount options
  };

  fileSystems."/mnt/Z_Drive" = {
  device = "192.168.211.174:/volume1/Z_Drive"; # NFS server and exported path
  fsType = "nfs"; # Filesystem type
  options = [ "defaults" ]; # Mount options
  };

  # Select internationalisation properties.
  # i18n.defaultLocale = "en_US.UTF-8";
  # console = {
  #   font = "Lat2-Terminus16";
  #   keyMap = "us";
  #   useXkbConfig = true; # use xkbOptions in tty.
  # };

  # Enable the X11 windowing system.
  # services.xserver.enable = true;

  # Configure keymap in X11
  services.xserver.layout = "us";
  # services.xserver.xkbOptions = "eurosign:e,caps:escape";

  # Enable CUPS to print documents.
  # services.printing.enable = true;

  # Enable sound.
  # sound.enable = true;
  # hardware.pulseaudio.enable = true;

  # Enable touchpad support (enabled default in most desktopManager).
  # services.xserver.libinput.enable = true;

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.xmike = {
    isNormalUser = true;
    initialPassword = "Password99";
    extraGroups = [ "wheel" ]; # Enable ‘sudo’ for the user.
    packages = with pkgs; [
      # firefox
      # tree
    ];
  };

  # Enable passwordless sudo
  security.sudo.extraRules= [
    {  users = [ "xmike" ];
      commands = [
         { command = "ALL" ;
           options= [ "NOPASSWD" ]; # "SETENV" # Adding the following could be>
        }
      ];
    }
  ];

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
    docker
    git
    nano
    neofetch
    wget
  ];

  # Enable the Docker daemon
  virtualisation.docker.enable = true;
  virtualisation.docker.daemon.settings = {
    live-restore = false;
  };

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  # List services that you want to enable:
  services.qemuGuest.enable = true;
  # services.kdeconnect.enable = true;

  # Enable the OpenSSH daemon.
  services.openssh.enable = true;

  # Open ports in the firewall.
  networking.firewall.allowedTCPPorts = [
    2377
    5201
    7946
  ];
  networking.firewall.allowedUDPPorts = [
    4789
    5201
    7946
  ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

  # Copy the NixOS configuration file and link it from the resulting system
  # (/run/current-system/configuration.nix). This is useful in case you
  # accidentally delete configuration.nix.
  # system.copySystemConfiguration = true;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It's perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "23.05"; # Did you read the comment?

}
