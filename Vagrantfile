# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "centos/7"
  config.disksize.size = '80GB'

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "public_network",
    use_dhcp_assigned_default_route: true

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
   config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
     vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
     vb.memory = "6144"
     vb.cpus = 4
   end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  #config.ssh.username = 'root'
  #config.ssh.password = 'vagrant'
  #config.ssh.insert_key = 'true'

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
   config.vm.provision "shell", inline: <<-SHELL
     sudo parted /dev/sda mkpart primary 42.9GB 100% set 4 lvm on quit
     sudo pvcreate /dev/sda4
     sudo vgextend VolGroup00 /dev/sda4
     sudo lvextend /dev/mapper/VolGroup00-LogVol00 -rl +100%FREE
     sudo xfs_growfs /dev/VolGroup00/LogVol00
     sudo yum -y update
     sudo yum -y install yum-utils
     sudo yum -y groupinstall development
     sudo yum -y install cmake
     sudo yum -y install libaio-devel
     sudo yum -y install ncurses-devel
     sudo yum -y install readline readline-devel
     sudo yum -y install pam pam-devel
     sudo yum -y install openssl openssl-devel
     sudo yum -y install libev libev-devel
     sudo yum -y install libgcrypt libgcrypt-devel
     sudo yum -y install libcurl libcurl-devel
     sudo yum -y install wget
     sudo yum -y install vim
     sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
     sudo yum -y install http://www.percona.com/downloads/percona-release/redhat/0.1-4/percona-release-0.1-4.noarch.rpm
     sudo yum -y update
     sudo yum -y install qpress
     sudo yum -y install jemalloc
     sudo yum -y install percona-toolkit
     sudo yum -y install sysbench
     sudo yum -y install python35u
     sudo yum -y install python35u-pip
     sudo yum -y install python35u-devel
     sudo yum -y install python35u-tkinter
     sudo yum -y install xauth
     sudo pip3.5 install setuptools -U pip setuptools
     sudo pip3.5 install memory_profiler
     sudo pip3.5 install psutil
     sudo pip3.5 install matplotlib
     sudo pip3.5 install virtualenv
     cd /home/vagrant
     virtualenv -p /usr/bin/python3.5 py_3_5_autoxtrabackup
     cd /vagrant
     sudo /home/vagrant/py_3_5_autoxtrabackup/bin/python setup.py install
     sudo sed -i "0,/^[ \t]*testpath[ \t]*=.*$/s|^[ \t]*testpath[ \t]*=.*$|testpath=\/home\/vagrant\/XB_TEST\/server_dir|" /home/vagrant/.autoxtrabackup/autoxtrabackup.cnf
     cd /home/vagrant
     sudo chown -R vagrant:vagrant *
     touch python-sudo.sh
     echo "#!/bin/bash" > python-sudo.sh
     echo 'sudo /usr/bin/python3.5 "$@"' >> python-sudo.sh
     chmod +x python-sudo.sh
     git clone https://github.com/sstephenson/bats.git
     cd bats
     ./install.sh /usr/local
     cd /tmp
     sudo chown -R vagrant:vagrant *
     cd /vagrant/test
     source /home/vagrant/py_3_5_autoxtrabackup/bin/activate
     /usr/local/bin/bats prepare_env.bats
     chown -R vagrant:vagrant *
SHELL
end
