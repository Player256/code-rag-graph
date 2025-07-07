CREATE_FILE_NODE = """
MERGE (f:File {path: $path})
"""

CREATE_IMPORT_RELATIONSHIP = """
MATCH (f:File {path: $file_path})
MERGE (m:Module {name: $module_name})
MERGE (f)-[:IMPORTS]->(m)
"""

CREATE_CLASS_NODE_AND_RELATIONSHIP = """
MATCH (f:File {path: $file_path})
MERGE (c:Class {name: $class_name, file_path: $file_path})
MERGE (f)-[:DEFINES_CLASS]->(c)
"""

CREATE_FUNCTION_NODE_AND_RELATIONSHIP = """
MATCH (parent {file_path: $file_path})
WHERE (parent:File) OR (parent:Class AND parent.name = $parent_name)
MERGE (func:Function {name: $function_name, file_path: $file_path})
MERGE (parent)-[:DEFINES_FUNCTION]->(func)
"""

CREATE_CALL_RELATIONSHIP = """
MATCH (caller:Function {name: $caller_name, file_path: $file_path})
MATCH (callee:Function {name: $callee_name})
MERGE (caller)-[:CALLS]->(callee)
"""

CREATE_INHERITANCE_RELATIONSHIP = """
MATCH (child:Class {name: $child_class, file_path: $file_path})
MATCH (parent:Class {name: $parent_class})
MERGE (child)-[:INHERITS_FROM]->(parent)
"""
