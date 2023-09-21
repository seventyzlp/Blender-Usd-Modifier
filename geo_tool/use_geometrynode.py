#initialize geometry_nodes node group
def geometry_nodes_node_group():
	geometry_nodes= bpy.data.node_groups.new(type = 'GeometryNodeTree', name = "Geometry Nodes")

	#initialize geometry_nodes nodes
	#geometry_nodes inputs
	#input Geometry
	geometry_nodes.inputs.new('NodeSocketGeometry', "Geometry")
	geometry_nodes.inputs[0].attribute_domain = 'POINT'


	#node Group Input
	group_input = geometry_nodes.nodes.new("NodeGroupInput")

	#geometry_nodes outputs
	#output Geometry
	geometry_nodes.outputs.new('NodeSocketGeometry', "Geometry")
	geometry_nodes.outputs[0].attribute_domain = 'POINT'


	#node Group Output
	group_output = geometry_nodes.nodes.new("NodeGroupOutput")

	#initialize nodegroup node group
	def nodegroup_node_group():
		nodegroup= bpy.data.node_groups.new(type = 'GeometryNodeTree', name = "NodeGroup")

		#initialize nodegroup nodes
		#node Mesh Circle
		mesh_circle = nodegroup.nodes.new("GeometryNodeMeshCircle")
		mesh_circle.fill_type = 'NONE'
		#Vertices
		mesh_circle.inputs[0].default_value = 5
		#Radius
		mesh_circle.inputs[1].default_value = 2.8999998569488525

		#nodegroup inputs
		#input Instance
		nodegroup.inputs.new('NodeSocketGeometry', "Instance")
		nodegroup.inputs[0].attribute_domain = 'POINT'


		#node Group Input
		group_input_1 = nodegroup.nodes.new("NodeGroupInput")

		#node Instance on Points
		instance_on_points = nodegroup.nodes.new("GeometryNodeInstanceOnPoints")
		#Selection
		instance_on_points.inputs[1].default_value = True
		#Pick Instance
		instance_on_points.inputs[3].default_value = False
		#Instance Index
		instance_on_points.inputs[4].default_value = 0
		#Rotation
		instance_on_points.inputs[5].default_value = (0.0, -1.815142273902893, 0.0)
		#Scale
		instance_on_points.inputs[6].default_value = (1.0, 1.0, 1.0)

		#node Realize Instances
		realize_instances = nodegroup.nodes.new("GeometryNodeRealizeInstances")

		#nodegroup outputs
		#output Instances
		nodegroup.outputs.new('NodeSocketGeometry', "Instances")
		nodegroup.outputs[0].attribute_domain = 'POINT'


		#node Group Output
		group_output_1 = nodegroup.nodes.new("NodeGroupOutput")


		#Set locations
		mesh_circle.location = (-476.6399841308594, 18.05167579650879)
		group_input_1.location = (-753.0822143554688, -58.85465621948242)
		instance_on_points.location = (-158.1013946533203, -34.660335540771484)
		realize_instances.location = (225.0499267578125, -29.650650024414062)
		group_output_1.location = (492.4991149902344, -16.38978385925293)

		#Set dimensions
		mesh_circle.width, mesh_circle.height = 140.0, 100.0
		group_input_1.width, group_input_1.height = 140.0, 100.0
		instance_on_points.width, instance_on_points.height = 140.0, 100.0
		realize_instances.width, realize_instances.height = 140.0, 100.0
		group_output_1.width, group_output_1.height = 140.0, 100.0

		#initialize nodegroup links
		#mesh_circle.Mesh -> instance_on_points.Points
		nodegroup.links.new(mesh_circle.outputs[0], instance_on_points.inputs[0])
		#group_input_1.Instance -> instance_on_points.Instance
		nodegroup.links.new(group_input_1.outputs[0], instance_on_points.inputs[2])
		#realize_instances.Geometry -> group_output_1.Instances
		nodegroup.links.new(realize_instances.outputs[0], group_output_1.inputs[0])
		#instance_on_points.Instances -> realize_instances.Geometry
		nodegroup.links.new(instance_on_points.outputs[0], realize_instances.inputs[0])
		return nodegroup

	nodegroup = nodegroup_node_group()

	#node Group
	group = geometry_nodes.nodes.new("GeometryNodeGroup")
	group.node_tree = bpy.data.node_groups["NodeGroup"]


	#Set locations
	group_input.location = (-343.6367492675781, 21.69157600402832)
	group_output.location = (418.3838806152344, -8.503191947937012)
	group.location = (70.24053192138672, 8.394022941589355)

	#Set dimensions
	group_input.width, group_input.height = 140.0, 100.0
	group_output.width, group_output.height = 140.0, 100.0
	group.width, group.height = 140.0, 100.0

	#initialize geometry_nodes links
	#group_input.Geometry -> group.Instance
	geometry_nodes.links.new(group_input.outputs[0], group.inputs[0])
	#group.Instances -> group_output.Geometry
	geometry_nodes.links.new(group.outputs[0], group_output.inputs[0])
	return geometry_nodes

geometry_nodes = geometry_nodes_node_group()

