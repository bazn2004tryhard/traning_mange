from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseServerError
from django.conf import settings  # To potentially get RDF file path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.plugins.sparql import prepareQuery
from .university_ontology import query_prerequisite_graph_test, query_prerequisite_graph, query_curriculum
import json

@login_required()
def course_graph_view(request):
    student = request.user.student
    student_id = str(student.pk)
    graph_result = query_prerequisite_graph(student_id)

    return render(request, 'course_register/goiythminh.html', {
        "graph_data": json.dumps(graph_result["graph"]),
        "low_score_courses": json.dumps(graph_result["low_score_courses"]),
    })

#------------------

@login_required()
def curriculumGraph(request):
    student = request.user.student
    student_id = str(student.pk)
    graph_result = query_curriculum(student_id)

    return render(request, 'trainingprogram/training_program_graph.html', {
        "graph_data": json.dumps(graph_result["graph"]),
    })
