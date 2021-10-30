from dawndoor.app import main
from dawndoor.data import get_network
from dawndoor.wifi import start_ap, stop_ap

network_config = get_network()
if not network_config or network_config.get('can_start_ap', True):
    start_ap()
else:
    stop_ap()

main()
