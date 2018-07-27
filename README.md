# OpenStack object	storage
OpenStack object	storage	using	Python. An OpenStack	 object	 storage	 (e.g.,	 the	 Swift	 object	 storage	 project)	 stores	and	retrieves	objects	(i.e.,	files)	on	a	distributed	file	systems	with	scale	and	provides	software-defined-storage	 (SDS), which	 is	 scalable,	 durable,	 available,	manageable,	flexible,	adaptable,	open,	economic,	and	eventually	consistent.
The	following	processes	are	implemented:
a) proxy	process	communicates	with	external	clients,	and	accepts download,	list,	upload and	delete	operations
b) routing process	finds	storage	location	using	consistent	hashing
c) storage	process	stores	objects	and	metadata
d) consistency	process ensures	data	integrity	and	availability	by	finding	failed	drives	 or	 corrupted	 data,	 and	 replicating objects	 to	 a	 preset	 number	 of	copies,	by	default	2

Command-line arguments:
$ server 16 129.210.16.80 129.210.16.81 129.210.16.83, 129.210.16.86
$ client 129.210.16.80 9999

The	following commands are supported:
• download	<user/object> - display	where	the	<user/object> is	saved
• list	<user> - display	the	<user>’s objects/files in	“ls	–lrt”	format
• upload	<user/object> - display	which	disks	<user/object>	is	saved
• delete	<user/object> - display	a	confirmation
• add	<disk> - display	new	partitions	with	all	<user/object>	within
• remove	<disk>- display	new	partitions	with	all	<user/object>	within
