# university_ontology.py
from rdflib import Graph, Namespace, Literal

# university_ontology.py
from rdflib import Graph, Namespace, Literal, RDF
from owlrl import DeductiveClosure, RDFS_OWLRL_Semantics

def query_prerequisite_graph_test():
    g = Graph()
    g.parse("rdf_data/university_data.rdf")

    UNI = Namespace("http://www.semanticweb.org/admin/ontologies/2025/4/university-ontology-31#")

    query = f"""
    PREFIX uni: <{UNI}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    CONSTRUCT {{
        ?previous_course uni:isPrerequisiteFor ?current_course .
        ?current_course uni:isPrerequisiteFor ?next_course .
    }}
    WHERE {{
        ?current_course uni:hasPrerequisite ?previous_course ;
                        uni:isPrerequisiteFor ?next_course .
    }}
    """

    result_graph = g.query(query)

    triples = []
    for s, p, o in result_graph.graph:
        triples.append({
            "source": s.split("#")[-1],
            "relation": p.split("#")[-1],
            "target": o.split("#")[-1]
        })

    print("⚙️ Debug – Triples:", triples)
    return triples

#----------------

# Quan hệ tiên quyết các môn đã học để gợi ý điểm kém
def query_prerequisite_graph(student_id: str):
    g = Graph()
    g.parse("rdf_data/university-ontology-31.rdf")
    g.parse("rdf_data/university_data.rdf")
    DeductiveClosure(RDFS_OWLRL_Semantics).expand(g)

    UNI = Namespace("http://www.semanticweb.org/admin/ontologies/2025/4/university-ontology-31#")

    query = f"""
    PREFIX uni: <{UNI}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    CONSTRUCT {{
        ?previous_course uni:isPrerequisiteFor ?current_course .
        ?current_course uni:isPrerequisiteFor ?next_course .
    }}
    WHERE {{
        ?student uni:studentID "{student_id}"^^xsd:string ;
                uni:hasAchievedGrade [uni:forCourse ?current_course] .

        ?current_course uni:hasPrerequisite ?previous_course ;
                    uni:isPrerequisiteFor ?next_course .
    }}
    """

    result_graph = g.query(query)

    triples = []
    for s, p, o in result_graph.graph:
        triples.append({
            "source": s.split("#")[-1],
            "relation": p.split("#")[-1],
            "target": o.split("#")[-1]
        })

    # Truy vấn lấy các môn điểm kém (< 4)
    low_score_query = f"""
    PREFIX uni: <{UNI}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?course ?final_exam_score
    WHERE {{
        ?student a uni:Student ;
                 uni:studentID "{student_id}"^^xsd:string ;
                 uni:hasAchievedGrade ?grade.

        ?grade uni:forCourse ?course ;
               uni:finalExamScore ?final_exam_score.

        FILTER(xsd:decimal(?final_exam_score) < 4)
    }}
    """

    # Chạy SELECT query (trên cùng graph g)
    low_score_results = g.query(low_score_query)
    # Phân tích kết quả select
    low_score_courses = set()
    for row in low_score_results:
        course_uri = row.course
        low_score_courses.add(course_uri.split("#")[-1])

    print(f"🎯 {len(triples)} triples found for student {student_id}")
    context = {
            "graph": triples,
            "low_score_courses": list(low_score_courses)
    }
    return context

#-------------------------------

#Quan hẹ tien quyet cua chương trinh dao tao
def query_curriculum(student_id: str):
    g = Graph()
    g.parse("rdf_data/university-ontology-31.rdf")
    g.parse("rdf_data/university_data.rdf")
    DeductiveClosure(RDFS_OWLRL_Semantics).expand(g)

    UNI = Namespace("http://www.semanticweb.org/admin/ontologies/2025/4/university-ontology-31#")


    query = f"""
    PREFIX uni: <{UNI}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    select ?course_name ?next_course_name
    WHERE {{
        ?student a uni:Student ;
                 uni:studentID "{student_id}"^^xsd:string ;
                 uni:studiesMajor ?major ;
                 uni:academicEnrollmentYear ?enrollmentYear .

        ?major uni:offersTrainingProgram ?trainingProgram .
        ?trainingProgram uni:startYear ?startYear .
        FILTER (STR(?enrollmentYear) = STR(?startYear))
        ?trainingProgram uni:hasProgramComponent ?pcl.
        ?pcl uni:linksCourse ?course.
        ?course uni:courseName ?course_name;
                uni:isPrerequisiteFor [uni:courseName ?next_course_name]
    }}
    """

    query_result = g.query(query)
    triples = []
    for raw in query_result:
        triples.append({
            "source": str(raw[0]),
            "relation": 'Tiên quyết cho',
            "target": str(raw[1]),
        })
    context = {
        'graph' : triples,
    }
    return context




