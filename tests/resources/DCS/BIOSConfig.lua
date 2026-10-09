local BIOSConfig = {
	tcp_config = {
		{
			address = "*",
			port = 7778,
		},
	},
	udp_config = {
		{
			send_address = "239.255.50.10",
			send_port = 5010,
			receive_address = "*",
			receive_port = 7778,
		},
	},
	dev_mode = true,
	clean_logs = true,
	export_rate = 30,
	version = "0.8.3", -- set automatically, do not edit
}

return BIOSConfig
