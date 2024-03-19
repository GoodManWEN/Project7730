OPERATION_MAP = {
	'1': 'login',
	'2': 'get',
	'3': 'set',
	'4': 'ping',
	'5': 'delete',
	'6': 'mset',
    '7': 'sget',
}

QUERY_MDL = {
	'id': None,     # stock_name
	's_d': None,	# date_time
	'e_d': None,    # date_time
	'col': "",      # field columns
	'frq': 5,		# Aggregation frequency
	'adj': 3,       # adjust flag
	'lim': 2000,    # rows limit
}

QUERYS_MDL = {
	'id': None,     # stock_name
	'dt': None,	    # date_time
	'col': "",      # field columns
	'frq': 5,		# Aggregation frequency
	'adj': 3,       # adjust flag
}

LOGIN_MDL = {
	'usr': None,
	'pwd': None,
}

RES_MDL = {
	'code': 200,
	'msg': '',
	'data': '',
}

IST_MEL = {
	"id": None,			# stock_name
	"dt": None,			# datetime
	"pl": None          # payload
}