Simple web panel for managing Sing-Box protection on Asuswrt-Merlin routers (github.com/Dr4tez/sing-box4asus/). After installation, the panel is available at the routeraddress:5000.

FAST INSTALL: 
sh -c 'opkg update && opkg install python3 python3-pip && pip3 install flask && mkdir -p /jffs/addons/sing-box-script && cd /tmp && curl -L -o sing-box-script.zip https://github.com/andrey-levens/sing-box-asuswrt/archive/refs/heads/main.zip && unzip -o sing-box-script.zip && cp -r sing-box-asuswrt-main/* /jffs/addons/sing-box-script/ && rm -rf sing-box-script.zip sing-box-asuswrt-main && mkdir -p /jffs/scripts && AUTOSTART=/jffs/scripts/services-start && LINE="logger \"[autostart] Starting sing-box-script and app.py...\"\n(sleep 60 && /opt/bin/python3 /jffs/addons/sing-box-script/app.py >> /jffs/addons/sing-box-script/app.log 2>&1) &" && (grep -q "sing-box-script/app.py" $AUTOSTART || echo -e "$LINE" >> $AUTOSTART) && chmod +x $AUTOSTART && (sleep 1 && /opt/bin/python3 /jffs/addons/sing-box-script/app.py >> /jffs/addons/sing-box-script/app.log 2>&1) &'

FAST DELETE: 
sh -c 'AUTOSTART=/jffs/scripts/services-start; [ -f "$AUTOSTART" ] && sed -i "/sing-box-script\/app.py/d" $AUTOSTART; rm -f /jffs/addons/sing-box-script/app.py; logger "[uninstall] sing-box-script app.py удалён." &'

VERSION SCRIPT: 0.1 BETA

