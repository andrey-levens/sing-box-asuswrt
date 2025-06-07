Simple web panel for managing Sing-Box protection on Asuswrt-Merlin routers (github.com/Dr4tez/sing-box4asus/). After installation, the panel is available at the routeraddress:5000.

FAST INSTALL: 
curl -fsSL https://raw.githubusercontent.com/andrey-levens/sing-box-asuswrt/main/install_singbox.sh -o install_singbox.sh && chmod +x install_singbox.sh && ./install_singbox.sh

FAST DELETE: 
sh -c 'AUTOSTART=/jffs/scripts/services-start; [ -f "$AUTOSTART" ] && sed -i "/sing-box-script\/app.py/d" $AUTOSTART; rm -f /jffs/addons/sing-box-script/app.py; logger "[uninstall] sing-box-script app.py удалён." &'

SCRIPT VERSION: 0.1

