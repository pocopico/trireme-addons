#!/usr/bin/env sh
#
# Copyright (C) 2023 Ing <https://github.com/pocopico/>
#
# This is free software, licensed under the MIT License.
# See /LICENSE for more information.
#
# Description:
#
# This script is used to fix missing HW features dependencies in the ramdisk, and it will 
# be executed in the early stage of the boot process, before the main system is fully up. 
# It will check the CPU features and other hardware features, and disable the loading of 
# kernel modules that are not supported by the hardware. This can help to avoid system
# instability or crashes caused by loading unsupported kernel modules.
#
# Change Log :
#
#
# shellcheck disable=SC2034

if [ -z ${1} ] ; then
echo "Invalid option specified expected at least on of the following : early/late/patches/modules/jrExit"
exit 0
fi

GKV=$([ -x "/usr/syno/bin/synogetkeyvalue" ] && echo "/usr/syno/bin/synogetkeyvalue" || echo "/bin/get_key_value")
SKV=$([ -x "/usr/syno/bin/synosetkeyvalue" ] && echo "/usr/syno/bin/synosetkeyvalue" || echo "/bin/set_key_value")

if [ ${1} = "early" ]; then
echo "Entering Early Stage....."

    for file in "lrz" "lsz" "ttyd" "tcrp-discover" "sed" "sshx" "jq" "dufs" ; do
      [ -f "/exts/misc/${file}" ] && cp -pf "/exts/misc/${file}" "/usr/bin/${file}"
      chmod 755 "/usr/bin/${file}"
    done

echo -n "Starting ttyd, listening on port: 7681"
[ $(netstat -an  |grep 7681 |wc -l) -gt 1 ] || /exts/misc/ttyd -W login -f root > /dev/null 2>&1 &
[ $(netstat -an  |grep 7681 |wc -l) -gt 1 ] && echo "-> ttyd started" || echo "-> ttyd start failed"
echo -n "Starting tcrp-discover"
[ $(netstat -an  |grep 7780 |wc -l) -gt 1 ] || /exts/misc/tcrp-discover > /dev/null 2>&1 &
[ $(netstat -an  |grep 7780 |wc -l) -gt 1 ] && echo "-> tcrp-discover started" || echo "-> tcrp-discover start failed"
echo -n "Starting DUFS, listening on port: 7304"
[ $(netstat -an  |grep 7304 |wc -l) -gt 1 ] || /exts/misc/dufs -A -p 7304 / >/dev/null 2>&1 & 
[ $(netstat -an  |grep 7304 |wc -l) -gt 1 ] && echo "-> dufs started" || echo "-> dufs start failed"


# [CREATE][failed] Raidtool initsys
echo -n "Patching scemd....."
SO_FILE="/usr/syno/bin/scemd"      
[ ! -f "${SO_FILE}.bak" ] && cp -pf "${SO_FILE}" "${SO_FILE}.bak"
cp -pf "${SO_FILE}" "${SO_FILE}.tmp" 
/exts/misc/xxd -c "$(/exts/misc/xxd -p "${SO_FILE}.tmp" 2>/dev/null | wc -c)" -p "${SO_FILE}.tmp" 2>/dev/null |  /exts/misc/sed "s/2d6520302e39/2d6520312e32/" | /exts/misc/xxd -r -p >"${SO_FILE}" 2>/dev/null       
rm -f "${SO_FILE}.tmp"

#Removing root password 
/exts/misc/sed -i 's/^root:x:0:0/root::0:0/' /etc/passwd


fi

########## Recovery mode related setup, including webman pages and motd

if grep -q "recovery" /proc/cmdline ; then
echo "Recovery mode detected"

   for file in /exts/misc/*cgi ; do
     [ -f "${file}" ] && echo "Copying ${file} to /usr/syno/web/webman" && cp -pf "${file}" "/usr/syno/web/webman/"
   done
   
   if [ ! -f "/usr/syno/web/web_install.html" ]; then
    {
      echo "Trireme Recovery Mode"
      echo
      echo "Using terminal commands to modify system configs, execute external binary"
      echo "files, add files, or install unauthorized third-party apps may lead to system"
      echo "damages or unexpected behavior, or cause data loss. Make sure you are aware of"
      echo "the consequences of each command and proceed at your own risk."
      echo
      echo "Warning: Data should only be stored in shared folders. Data stored elsewhere"
      echo "may be deleted when the system is updated/restarted."
      echo
      echo "To 'Force re-install DSM': please visit http://<ip>:5000/web_install.html"
      echo "To 'System partition(/dev/md0) has been mounted to': /tmpRoot"
    } >/etc/motd

    cp -pf /usr/syno/web/web_index.html /usr/syno/web/web_install.html
    cp -pf /exts/misc/web_index.html /usr/syno/web/web_index.html

       if [ $(mount | grep -c "/dev/md0 on /tmpRoot") -eq 0 ]; then
       mkdir -p /tmpRoot
       mount /dev/md0 /tmpRoot
       fi 
   fi

echo "Recovery mode is ready"

fi


if [ "${1}" = "rcExit" ]; then
  echo "Installing addon misc - ${1}"

  # enable telnet
  /exts/misc/sed -i 's/^root:x:0:0/root::0:0/' /etc/passwd
  inetd

  # invalid_disks
  # method 1 # (block dsm system migrate)
  # SH_FILE="/usr/syno/share/get_hcl_invalid_disks.sh"
  # [ -f "${SH_FILE}" ] && cp -pf "${SH_FILE}" "${SH_FILE}.bak" && printf '#!/bin/sh\nexit 0\n' >"${SH_FILE}"
  # method 2
  while true; do [ ! -f "/tmp/installable_check_pass" ] && touch "/tmp/installable_check_pass"; sleep 1; done &  # using a while loop in case DSM is running in a VM

  # error message
  if [ ! -b /dev/synoboot ] || [ ! -b /dev/synoboot1 ] || [ ! -b /dev/synoboot2 ] || [ ! -b /dev/synoboot3 ]; then
    /exts/misc/sed -i 's/c("welcome","desc_install")/"Error: The bootloader disk is not successfully mounted, the installation will fail."/' /usr/syno/web/main.js 2>/dev/null
  fi

  # disable DisabledPortDisks
  /exts/misc/sed -i 's/^DisabledPortDisks=.*$/DisabledPortDisks=""/' /usr/syno/web/webman/get_state.cgi 2>/dev/null

  # reboot
  /exts/misc/sed -i 's/reboot$/reboot -f/' /usr/syno/web/webman/reboot.cgi 2>/dev/null

  # recovery
  if grep -wq "recovery" /proc/cmdline 2>/dev/null && [ -x /usr/syno/web/webman/recovery.cgi ]; then
    /usr/syno/web/webman/recovery.cgi
  fi

fi

if [ ${1} = "late" ]; then
echo "Entering Early Stage....."
echo "Script for fixing missing HW features dependencies"

killall tcrp-discover 2>/dev/null || true
killall ttyd 2>/dev/null || true
killall dufs 2>/dev/null || true

PLATFORM="$(uname -u | cut -d '_' -f2)"

cp /exts/misc/sed /tmpRoot/usr/bin/sed
chmod +x /tmpRoot/usr/bin/sed

SED_PATH='/tmpRoot/usr/bin/sed'
 
# lspci
mkdir -vp /tmpRoot/usr/local/share
cp -vpf /usr/local/share/pci.ids.gz /tmpRoot/usr/local/share/pci.ids.gz

# perform synoinfo.conf updates
echo "Setting synoinfo.conf values"
for KEY in $(cat "/exts/synoinfo.conf" 2>/dev/null | cut -d= -f1); do
  [ -z "${KEY}" ] && continue
  VALUE="$("${GKV}" /exts/synoinfo.conf "${KEY}")"
  echo "Setting ${KEY} to ${VALUE}"
  for F in "/tmpRoot/etc/synoinfo.conf" "/tmpRoot/etc.defaults/synoinfo.conf"; do "${SKV}" "${F}" "${KEY}" "${VALUE}"; done
done

######## CPU performance scaling

  mount -t sysfs sysfs /sys
  modprobe acpi-cpufreq
  if [ -f /tmpRoot/usr/lib/modules-load.d/70-cpufreq-kernel.conf ]; then
    CPUFREQ=$(ls -l /sys/devices/system/cpu/cpufreq/*/* 2>/dev/null | wc -l)
    if [ ${CPUFREQ} -eq 0 ]; then
      echo "CPU does NOT support CPU Performance Scaling, disabling"
      /exts/misc/sed -i 's/^acpi-cpufreq/# acpi-cpufreq/g' /tmpRoot/usr/lib/modules-load.d/70-cpufreq-kernel.conf
    else
      echo "CPU supports CPU Performance Scaling, enabling"
      /exts/misc/sed -i 's/^# acpi-cpufreq/acpi-cpufreq/g' /tmpRoot/usr/lib/modules-load.d/70-cpufreq-kernel.conf
      cp -vpf /usr/lib/modules/cpufreq_* /tmpRoot/usr/lib/modules/
    fi
  fi
  modprobe -r acpi-cpufreq
  umount /sys

######## fixcpufreq() 

    if [ $(mount 2>/dev/null | grep sysfs | wc -l) -eq 0 ]; then
        mount -t sysfs sysfs /sys
        [ -f /usr/lib/modules/processor.ko ] && insmod /tmpRoot/usr/lib/modules/processor.ko
        [ -f /usr/lib/modules/acpi-cpufreq.ko ] && insmod /tmpRoot/usr/lib/modules/acpi-cpufreq.ko
    fi
    # CPU performance scaling
    if [ -f /tmpRoot/usr/lib/modules-load.d/70-cpufreq-kernel.conf ]; then
        cpufreq=$(ls -ltr /sys/devices/system/cpu/cpufreq/* 2>/dev/null | wc -l)
        if [ $cpufreq -eq 0 ]; then
            echo "CPU does NOT support CPU Performance Scaling, disabling"
            ${SED_PATH} -i 's/^acpi-cpufreq/# acpi-cpufreq/g' /tmpRoot/usr/lib/modules-load.d/70-cpufreq-kernel.conf
        else
            echo "CPU supports CPU Performance Scaling, enabling"
            ${SED_PATH} -i 's/^# acpi-cpufreq/acpi-cpufreq/g' /tmpRoot/usr/lib/modules-load.d/70-cpufreq-kernel.conf
        fi
    fi
    umount /sys

########fixcrypto() 
# crc32c-intel
    if [ -f /tmpRoot/usr/lib/modules-load.d/70-crypto-kernel.conf ]; then
        CPUFLAGS=$(cat /proc/cpuinfo | grep flags | grep sse4_2 | wc -l)
        if [ $CPUFLAGS -gt 0 ]; then
            echo "CPU Supports SSE4.2, crc32c-intel should load"
        else
            echo "CPU does NOT support SSE4.2, crc32c-intel will not load, disabling"
            ${SED_PATH} -i 's/^crc32c-intel/# crc32c-intel/g' /tmpRoot/usr/lib/modules-load.d/70-crypto-kernel.conf
        fi
    fi

######### aesni-intel
    if [ -f /tmpRoot/usr/lib/modules-load.d/70-crypto-kernel.conf ]; then
        CPUFLAGS=$(cat /proc/cpuinfo | grep flags | grep aes | wc -l)
        if [ ${CPUFLAGS} -gt 0 ]; then
            echo "CPU Supports AES, aesni-intel should load"
        else
            echo "CPU does NOT support AES, aesni-intel will not load, disabling"
            ${SED_PATH} -i 's/support_aesni_intel="yes"/support_aesni_intel="no"/' /tmpRoot/etc.defaults/synoinfo.conf
            ${SED_PATH} -i 's/^aesni-intel/# aesni-intel/g' /tmpRoot/usr/lib/modules-load.d/70-crypto-kernel.conf
        fi
    fi

######## fixnvidia()
    # Nvidia GPU
    if [ -f /tmpRoot/usr/lib/modules-load.d/70-syno-nvidia-gpu.conf ]; then
        NVIDIADEV=$(cat /proc/bus/pci/devices | grep -i 10de | wc -l)
        if [ $NVIDIADEV -eq 0 ]; then
            echo "NVIDIA GPU is not detected, disabling "
            ${SED_PATH} -i 's/^nvidia/# nvidia/g' /tmpRoot/usr/lib/modules-load.d/70-syno-nvidia-gpu.conf
            ${SED_PATH} -i 's/^nvidia-uvm/# nvidia-uvm/g' /tmpRoot/usr/lib/modules-load.d/70-syno-nvidia-gpu.conf
        else
            echo "NVIDIA GPU is detected, nothing to do"
        fi
    fi

######## fixintelgpu()
    # Intel GPU
    GPU="$(LD_LIBRARY_PATH=/tmpRoot/lib64 /tmpRoot/bin/lspci -n | grep 0300 | cut -d " " -f 3 | /exts/misc/sed -e 's/://g')"
    if [ -f /tmpRoot/usr/lib/modules-load.d/70-video-kernel.conf ]; then
        INTELGPU=$(grep -i ${GPU} /exts/misc/pciids | wc -l)
        if [ $INTELGPU -eq 0 ]; then
            echo "Intel GPU is not detected ($GPU), disabling "
            ${SED_PATH} -i 's/^i915/# i915/g' /tmpRoot/usr/lib/modules-load.d/70-video-kernel.conf
        else
            echo "Intel GPU is detected ($GPU), nothing to do"
        fi
    fi


######## fixacpibutton()
    #button.ko

    if [ ! -d /proc/acpi ]; then
        echo "NO ACPI status is available, disabling button.ko"
        ${SED_PATH} -i 's/^button/# button/g' /tmpRoot/usr/lib/modules-load.d/70-video-kernel.conf
    fi

######## sdcard
  [ ! -f /tmpRoot/usr/lib/udev/script/sdcard.sh.bak ] && cp -vpf /tmpRoot/usr/lib/udev/script/sdcard.sh /tmpRoot/usr/lib/udev/script/sdcard.sh.bak
  printf '#!/bin/sh\nexit 0\n' >/tmpRoot/usr/lib/udev/script/sdcard.sh

######## beep
cp -vpf /usr/bin/beep /tmpRoot/usr/bin/beep
cp -vpdf /usr/lib/libubsan.so* /tmpRoot/usr/lib/

######## disable system home calling service
# systemd-modules-load SynoInitEth syno-oob-check-status syno_update_disk_logs
  rm -vf /tmpRoot/usr/lib/modules-load.d/70-network*.conf
  /exts/misc/sed -i 's|ExecStart=/|ExecStart=-/|g' /tmpRoot/usr/lib/systemd/system/systemd-modules-load.service 2>/dev/null
  /exts/misc/sed -i 's|ExecStart=/|ExecStart=-/|g' /tmpRoot/usr/lib/systemd/system/SynoInitEth.service 2>/dev/null
  /exts/misc/sed -i 's|ExecStart=/|ExecStart=-/|g' /tmpRoot/usr/lib/systemd/system/syno-oob-check-status.service 2>/dev/null
  /exts/misc/sed -i 's|ExecStart=/|ExecStart=-/|g' /tmpRoot/usr/lib/systemd/system/syno_update_disk_logs.service 2>/dev/null

######## getty
  for I in $(cat /proc/cmdline 2>/dev/null | grep -Eo 'getty=[^ ]+' | /exts/misc/sed 's/getty=//'); do
    TTYN="$(echo "${I}" | cut -d',' -f1)"
    BAUD="$(echo "${I}" | cut -d',' -f2 | cut -d'n' -f1)"
    echo "ttyS0 ttyS1 ttyS2" | grep -wq "${TTYN}" && continue

    mkdir -vp /tmpRoot/usr/lib/systemd/system/getty.target.wants
    if [ -n "${TTYN}" ] && [ -e "/dev/${TTYN}" ]; then
      echo "Make getty\@${TTYN}.service"
      cp -vpf /tmpRoot/usr/lib/systemd/system/serial-getty\@.service /tmpRoot/usr/lib/systemd/system/getty\@${TTYN}.service
      /exts/misc/sed -i "s|^ExecStart=.*|ExecStart=-/sbin/agetty %I ${BAUD:-115200} linux|" /tmpRoot/usr/lib/systemd/system/getty\@${TTYN}.service
      mkdir -vp /tmpRoot/usr/lib/systemd/system/getty.target.wants
      ln -vsf /usr/lib/systemd/system/getty\@${TTYN}.service /tmpRoot/usr/lib/systemd/system/getty.target.wants/getty\@${TTYN}.service
    fi
  done

fi


