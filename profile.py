# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Emulab specific extensions.
import geni.rspec.emulab as emulab
# Markdown
import geni.rspec.igext as IG

tourDescription = """
A single server node with a variable number of client nodes in a lan. You have the option of picking from one
of three Ubuntu standard images we provide, or just use the default (typically a recent
version of Ubuntu). You may also optionally pick the specific hardware type for
all the nodes in the lan. 
"""
tourInstructions = """
Instructions:
[Documentation](https://leaf.cmu.edu/build/html/index.html) for LEAF.
Leaf has been installed in ```/opt``` directory.
To run leaf, run ```sudo /opt/leaf/paper_experiments/femnist.sh /opt```
This will run leaf and place the results in the /opt directory.
"""

# Globals
class GLOBALS(object):
    LEAF_INSTALL_SCRIPT = "/usr/bin/sudo /local/repository/bin/leaf_install.sh"

# Create a portal context, needed to defined parameters
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Variable number of nodes.
pc.defineParameter("nodeCount", "Number of Clients", portal.ParameterType.INTEGER, 0,
                   longDescription="Leave as 0 for just the server. " + 
                   "NOTE: As of now, this is limited to 3 client nodes.")

# Pick your OS.
imageList = [
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD', 'UBUNTU 18.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU16-64-STD', 'UBUNTU 16.04')]

pc.defineParameter("osImage", "Select OS image",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList,
                   longDescription="Pick your favorite image.")

# Optional physical type for all nodes.
pc.defineParameter("phystype",  "Optional physical node type",
                   portal.ParameterType.STRING, "",
                   longDescription="Specify a physical node type (pc3000,d430,d710,etc) " +
                   "instead of letting the resource mapper choose for you.")

# Optionally create XEN VMs instead of allocating bare metal nodes.
pc.defineParameter("useVMs",  "Use VMs",
                   portal.ParameterType.BOOLEAN, False,
                   longDescription="Create XEN VMs instead of allocating bare metal nodes.")

# Optional link speed, normally the resource mapper will choose for you based on node availability
# pc.defineParameter("linkSpeed", "Link Speed",portal.ParameterType.INTEGER, 0,
#                   [(0,"Any"),(100000,"100Mb/s"),(1000000,"1Gb/s"),(10000000,"10Gb/s"),(25000000,"25Gb/s"),(100000000,"100Gb/s")],
#                   advanced=True,
#                   longDescription="A specific link speed to use for your lan. Normally the resource " +
#                   "mapper will choose for you based on node availability and the optional physical type.")
                   

# # Optional ephemeral blockstore
# pc.defineParameter("tempFileSystemSize", "Temporary Filesystem Size",
#                   portal.ParameterType.INTEGER, 0,advanced=True,
#                   longDescription="The size in GB of a temporary file system to mount on each of your " +
#                   "nodes. Temporary means that they are deleted when your experiment is terminated. " +
#                   "The images provided by the system have small root partitions, so use this option " +
#                   "if you expect you will need more space to build your software packages or store " +
#                   "temporary files.")
                   
# # Instead of a size, ask for all available space. 
pc.defineParameter("tempFileSystemMax",  "Temp Filesystem Max Space",
                    portal.ParameterType.BOOLEAN, False,
                    advanced=True,
                    longDescription="Instead of specifying a size for your temporary filesystem, " +
                    "check this box to allocate all available disk space. Leave the tempFileSystemSize above as zero (currently not included).")

pc.defineParameter("tempFileSystemMount", "Temporary Filesystem Mount Point",
                  portal.ParameterType.STRING,"/mydata",advanced=True,
                  longDescription="Mount the temporary file system at this mount point; in general you " +
                  "you do not need to change this, but we provide the option just in case your software " +
                  "is finicky.")

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()

# Check parameter validity.
numClients = params.nodeCount if params.nodeCount >= 1  else 0

# if params.tempFileSystemSize < 0 or params.tempFileSystemSize > 200:
#     pc.reportError(portal.ParameterError("Please specify a size greater then zero and " +
#                                          "less then 200GB", ["nodeCount"]))
pc.verifyParameters()

# Create link/lan.
if numClients == 1:
    lan = request.Link()
elif numClients > 1:
    lan = request.LAN()
    lan.best_effort = True
# if params.bestEffort:
#     lan.best_effort = True
# elif params.linkSpeed > 0:
#     lan.bandwidth = params.linkSpeed
# pass

# Process nodes, adding to link or lan.
numClients = numClients if numClients < 4 else 3
for i in range(numClients + 1):
    # Create a node and add it to the request
    if params.useVMs:
        name = "client-vm" + str(i) if i > 0 else "server-vm"
        node = request.XenVM(name)
    else:
        name = "client" + str(i) if i > 0 else "server"
        node = request.RawPC(name)
    if params.osImage:
        node.disk_image = params.osImage
    # Add to lan
    if numClients > 0:
        iface = node.addInterface("eth1")
        lan.addInterface(iface)
    # Optional hardware type.
    if params.phystype != "":
        node.hardware_type = params.phystype
    # Optional Blockstore
    if params.tempFileSystemMax:
        bs = node.Blockstore(name + "-bs", params.tempFileSystemMount)
        bs.size = "0GB"
        bs.placement = "any"
    node.addService(pg.Execute(shell="bash", command=GLOBALS.LEAF_INSTALL_SCRIPT))
        
    # Optional Blockstore
    # if params.tempFileSystemSize > 0 or params.tempFileSystemMax:
    #     bs = node.Blockstore(name + "-bs", params.tempFileSystemMount)
    #     if params.tempFileSystemMax:
    #         bs.size = "0GB"
    #     else:
    #         bs.size = str(params.tempFileSystemSize) + "GB"
    #         pass
    #     bs.placement = "any"
    #     pass

tour = IG.Tour()
tour.Description(IG.Tour.MARKDOWN, tourDescription)
tour.Instructions(IG.Tour.MARKDOWN, tourInstructions)
request.addTour(tour)

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
