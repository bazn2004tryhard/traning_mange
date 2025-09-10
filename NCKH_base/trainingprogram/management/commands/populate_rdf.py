'''
python manage.py populate_rdf
'''

import os
from django.core.management.base import BaseCommand
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# Import your Django models
from trainingprogram.models import (
    Faculty, Major, TrainingProgram, Course, OptionalGroup,
    CourseTrainingProgram, Role, User, UserRole, Lecturer, Student,
    Grade, Semester as DjangoSemester, Evaluate, Class as DjangoClass,  # Renamed to avoid conflict
    ClassSchedule, Enrollment, RegistrationHistory
)

# Define your ontology's namespace (from your OWX file)
MYONTO = Namespace("http://www.semanticweb.org/admin/ontologies/2025/2/untitled-ontology-14#")


class Command(BaseCommand):
    help = 'Populates an RDF graph from Django models based on the defined ontology.'

    def handle(self, *args, **options):
        g = Graph()

        # Bind namespaces for cleaner output (optional but good practice)
        g.bind("", MYONTO)
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)
        g.bind("xsd", XSD)

        self.stdout.write("Starting RDF population...")

        # --- Call functions to populate different parts of the graph ---
        self.populate_base_entities(g)
        self.populate_student_grade_relations(g)
        self.populate_course_prerequisites(g)
        self.populate_major_trainingprogram_relations(g)
        self.populate_course_trainingprogram_relations(g)  # For Course -> CTP
        self.populate_student_trainingprogram_relations(g)
        self.populate_student_major_relations(g)
        self.populate_course_group_relations(g)
        self.populate_group_credit_relations(g)
        # Add more population functions as needed for other entities/relations

        # --- Serialize the graph to a file ---
        # Determine the output path. You might want to make this configurable.
        # For now, let's put it in the project root or a specific 'rdf_data' directory.

        # Create rdf_data directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                                  'rdf_data')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, "populated_data.rdf")

        g.serialize(destination=output_file, format="xml")  # Or "turtle", "n3", etc.
        self.stdout.write(self.style.SUCCESS(f"Successfully populated RDF graph to {output_file}"))

    # --- Helper methods to create URIs ---
    def student_uri(self, student_id):
        return URIRef(MYONTO[f"Student_{student_id}"])

    def course_uri(self, course_id):
        return URIRef(MYONTO[f"Course_{course_id}"])

    def major_uri(self, major_id):
        return URIRef(MYONTO[f"Major_{major_id}"])

    def optional_group_uri(self, group_id):
        return URIRef(MYONTO[f"OptionalGroup_{group_id}"])

    def training_program_uri(self, program_id):
        return URIRef(MYONTO[f"TrainingProgram_{program_id}"])

    def course_training_program_uri(self, ctp_pk):  # Assuming ctp has a .pk
        return URIRef(MYONTO[f"CourseTrainingProgram_{ctp_pk}"])

    def grade_instance_uri(self, grade_id):
        return URIRef(MYONTO[f"GradeInstance_{grade_id}"])  # To distinguish from the Grade class

    # --- Population methods for specific triples ---

    def populate_base_entities(self, g):
        self.stdout.write("Populating base entities (Student, Course, Major, OptionalGroup)...")

        # Students
        for student in Student.objects.all():
            s_uri = self.student_uri(student.StudentID)
            g.add((s_uri, RDF.type, MYONTO.Student))
            # Add other student attributes if needed, e.g., name
            if student.Fullname:
                g.add((s_uri, MYONTO.hasStudentName, Literal(student.Fullname, datatype=XSD.string)))
            # Your OWX has StudentID as a UUIDField, which is the identifier for the URI.
            # If you wanted to add the ID as a literal property:
            # g.add((s_uri, MYONTO.hasStudentID_literal, Literal(str(student.StudentID), datatype=XSD.string))) 
            # But typically, the URI itself is the identifier.

        # Courses
        for course in Course.objects.all():
            c_uri = self.course_uri(course.course_id)
            g.add((c_uri, RDF.type, MYONTO.Course))
            g.add((c_uri, MYONTO.hasCourseName, Literal(course.course_name, datatype=XSD.string)))
            g.add((c_uri, MYONTO.hasCredit, Literal(course.credits, datatype=XSD.integer)))
            # Add other course attributes if defined in OWX (theory_hours, etc.)
            # g.add((c_uri, MYONTO.hasCourseID_literal, Literal(course.course_id, datatype=XSD.string)))

        # Majors
        for major in Major.objects.all():
            m_uri = self.major_uri(major.major_id)
            g.add((m_uri, RDF.type, MYONTO.Major))
            g.add((m_uri, MYONTO.hasMajorName, Literal(major.major_name, datatype=XSD.string)))
            # g.add((m_uri, MYONTO.hasMajorID_literal, Literal(major.major_id, datatype=XSD.string)))

        # OptionalGroups (GroupCourse)
        for og in OptionalGroup.objects.all():
            og_uri = self.optional_group_uri(og.id)  # Using UUID pk
            g.add((og_uri, RDF.type, MYONTO.OptionalGroup))
            g.add((og_uri, MYONTO.hasName, Literal(og.group_name, datatype=XSD.string)))  # Assuming generic hasName
            if og.description:
                g.add((og_uri, MYONTO.hasDecription, Literal(og.description, datatype=XSD.string)))
            # g.add((og_uri, MYONTO.hasOptionalGroupID_literal, Literal(str(og.id), datatype=XSD.string)))

        # TrainingPrograms (needed for relations)
        for tp in TrainingProgram.objects.all():
            tp_uri = self.training_program_uri(tp.program_id)
            g.add((tp_uri, RDF.type, MYONTO.TrainingProgram))
            g.add((tp_uri, MYONTO.hasName, Literal(tp.program_name, datatype=XSD.string)))  # Assuming generic hasName

        # CourseTrainingProgram instances (needed for relations)
        for ctp in CourseTrainingProgram.objects.all():
            ctp_i_uri = self.course_training_program_uri(ctp.pk)  # Using Django's auto PK
            g.add((ctp_i_uri, RDF.type, MYONTO.CourseTrainingProgram))
            # Link CTP to its Course and Program
            if ctp.course:
                g.add(
                    (ctp_i_uri, MYONTO.belongsToCourse, self.course_uri(ctp.course.course_id)))  # Or hasCourse from CTP
            if ctp.program:
                g.add((ctp_i_uri, MYONTO.belongsToTrainingProgram,
                       self.training_program_uri(ctp.program.program_id)))  # Or hasTrainingProgram from CTP
            # Add semester, course_type if properties exist in OWX for CTP
            g.add((ctp_i_uri, MYONTO.hasSemester, Literal(ctp.semester, datatype=XSD.integer)))
            g.add((ctp_i_uri, MYONTO.hasCourseType,
                   Literal(ctp.course_type, datatype=XSD.string)))  # Or integer if types are numeric

    def populate_student_grade_relations(self, g):
        self.stdout.write("Populating Student-Grade-Course relations...")
        # Your request: IDStudent hasGrade IDCourse
        # OWX seems to model this via a Grade instance:
        # Course --hasGrade--> GradeInstance --hasStudentGrade--> Student
        # GradeInstance --belongsToCourse--> Course
        # Let's try to fulfill your direct request, but also show the OWX-aligned way.

        for grade_record in Grade.objects.select_related('student', 'course').all():
            student_uri_val = self.student_uri(grade_record.student.StudentID)
            course_uri_val = self.course_uri(grade_record.course.course_id)

            # Fulfilling "IDStudent hasGrade IDCourse" directly (you might need to define 'studentHasGradeForCourse' in OWX)
            # This is a simplification. The predicate MYONTO.hasGrade in your OWX has Domain: Course, Range: Grade.
            # So, semantically, a Student cannot directly "hasGrade" a Course according to that definition.
            # You might want a custom predicate like MYONTO.studentTakesCourse or similar.
            # For now, let's use a placeholder, assuming you want this direct link for querying.
            # Consider adding a predicate like `studentAchievedGradeInCourse`
            # g.add((student_uri_val, MYONTO.achievedGradeIn, course_uri_val)) # Example custom predicate

            # More OWX-aligned approach: Create a Grade instance
            grade_inst_uri = self.grade_instance_uri(grade_record.GradeID)
            g.add((grade_inst_uri, RDF.type, MYONTO.Grade))  # This is an instance of the Grade class

            # Link Grade instance to Student and Course
            # OWX: Grade --hasStudentGrade--> Student (Inverse: Student --isStudentForGrade--> Grade)
            g.add((grade_inst_uri, MYONTO.hasStudentGrade, student_uri_val))

            # OWX: Course --hasGrade--> Grade (Instance) (Inverse: GradeInstance --isGradeOf--> Course / belongsToCourse)
            # So, a Course has a Grade instance.
            g.add((course_uri_val, MYONTO.hasGrade, grade_inst_uri))  # As per OWX Domain/Range of hasGrade

            # Add actual scores to the Grade instance
            # Your OWX has hasContinueAssScore & hasFinalExamScore with Domain: Course.
            # This is semantically problematic if scores are per student. Scores should be on the Grade instance.
            # Assuming you'll adjust OWX or interpret these properties for Grade instances:
            if grade_record.ContinuosAssScore is not None:
                g.add((grade_inst_uri, MYONTO.hasContinueAssScore,
                       Literal(grade_record.ContinuosAssScore, datatype=XSD.float)))
            if grade_record.FinalExamScore is not None:
                g.add((grade_inst_uri, MYONTO.hasFinalExamScore,
                       Literal(grade_record.FinalExamScore, datatype=XSD.float)))
            if grade_record.Result:
                g.add((grade_inst_uri, MYONTO.hasResult, Literal(grade_record.Result, datatype=XSD.string)))
            # Add other Grade attributes (Semester, AcademyYear, TestTime) if properties exist on MYONTO.Grade

    def populate_course_prerequisites(self, g):
        self.stdout.write("Populating Course-Prerequisite relations...")
        # IDCourse hasPrequisite IDCourse
        for course in Course.objects.prefetch_related('prerequisites').all():
            c_uri = self.course_uri(course.course_id)
            for prereq in course.prerequisites.all():
                prereq_uri = self.course_uri(prereq.course_id)
                # OWX has: ObjectProperty IRI="#hasPrerequisite" Domain: Course, Range: Class (Course is a subclass of Class)
                # OWX also has: ObjectProperty IRI="#isPrerequisiteOf"
                # This seems correct.
                g.add((c_uri, MYONTO.hasPrerequisite, prereq_uri))

    def populate_major_trainingprogram_relations(self, g):
        self.stdout.write("Populating Major-TrainingProgram relations...")
        # IDMajor hasTrainingProgram IDTrainingProgram
        for major in Major.objects.prefetch_related('trainingprogram_set').all():
            m_uri = self.major_uri(major.major_id)
            for tp in major.trainingprogram_set.all():  # trainingprogram_set is the reverse relation
                tp_uri = self.training_program_uri(tp.program_id)
                # OWX: ObjectProperty IRI="#hasTrainingProgram" Domain: Major, Range: TrainingProgram
                # This is correct.
                g.add((m_uri, MYONTO.hasTrainingProgram, tp_uri))

    def populate_course_trainingprogram_relations(self, g):
        self.stdout.write("Populating Course-CourseTrainingProgram relations...")
        # IDCourse hasTrainingProgram IDCourseTrainingProgram (instance)
        # OWX: ObjectProperty IRI="#hasCourseTrainingProgram" Domain: TrainingProgram, Range: CourseTrainingProgram
        # This means a TrainingProgram has a CTP instance.
        # Your request is Course -> CTP instance. This needs a custom predicate or re-evaluation.
        # Let's assume you want to link a Course to the CTP instances it's part of.
        # Predicate could be: MYONTO.participatesInViaCTP

        for ctp in CourseTrainingProgram.objects.select_related('course', 'program').all():
            if ctp.course:
                c_uri = self.course_uri(ctp.course.course_id)
                ctp_i_uri = self.course_training_program_uri(ctp.pk)
                # You'll need to define this predicate in your OWX if it doesn't exist
                # e.g., <owl:ObjectProperty rdf:about="&myonto;courseIsPartOfCTP">
                #         <rdfs:domain rdf:resource="&myonto;Course"/>
                #         <rdfs:range rdf:resource="&myonto;CourseTrainingProgram"/>
                #       </owl:ObjectProperty>
                g.add((c_uri, MYONTO.courseIsPartOfCTP, ctp_i_uri))  # Custom predicate needed

                # Also, the CTP instance is related to the Training Program
                # OWX: TrainingProgram hasCourseTrainingProgram CourseTrainingProgram (Instance)
                if ctp.program:
                    tp_uri_val = self.training_program_uri(ctp.program.program_id)
                    g.add((tp_uri_val, MYONTO.hasCourseTrainingProgram, ctp_i_uri))  # This matches OWX

    def populate_student_trainingprogram_relations(self, g):
        self.stdout.write("Populating Student-TrainingProgram relations...")
        # IDStudent hasTrainingProgram IDTrainingProgram
        # This is indirect: Student -> Major -> TrainingProgram
        for student in Student.objects.select_related('major__faculty').all():  # Eager load major
            if student.major:
                s_uri = self.student_uri(student.StudentID)
                # Get TPs for the student's major
                for tp in TrainingProgram.objects.filter(major=student.major):
                    tp_uri = self.training_program_uri(tp.program_id)
                    # OWX: hasTrainingProgram is Domain: Major.
                    # Need a predicate like MYONTO.studentEnrolledInTrainingProgram
                    # e.g. <owl:ObjectProperty rdf:about="&myonto;studentEnrolledInTrainingProgram">
                    #        <rdfs:domain rdf:resource="&myonto;Student"/>
                    #        <rdfs:range rdf:resource="&myonto;TrainingProgram"/>
                    #      </owl:ObjectProperty>
                    g.add((s_uri, MYONTO.studentEnrolledInTrainingProgram, tp_uri))  # Custom predicate

    def populate_student_major_relations(self, g):
        self.stdout.write("Populating Student-Major relations...")
        # IDStudent hasMajor IDMajor
        for student in Student.objects.select_related('major').all():
            if student.major:
                s_uri = self.student_uri(student.StudentID)
                m_uri = self.major_uri(student.major.major_id)
                # OWX: belongsToMajor Domain: TrainingProgram.
                # Need a predicate like MYONTO.studentBelongsToMajor or studentHasMajor
                # e.g. <owl:ObjectProperty rdf:about="&myonto;studentHasMajor">
                #        <rdfs:domain rdf:resource="&myonto;Student"/>
                #        <rdfs:range rdf:resource="&myonto;Major"/>
                #      </owl:ObjectProperty>
                g.add((s_uri, MYONTO.studentHasMajor, m_uri))  # Custom predicate

    def populate_course_group_relations(self, g):
        self.stdout.write("Populating Course-OptionalGroup relations...")
        # IDCourse hasGroup IDGroup (OptionalGroup)
        # This relation is via CourseTrainingProgram: Course -> CTP -> OptionalGroup
        for ctp in CourseTrainingProgram.objects.select_related('course', 'option_G').all():
            if ctp.course and ctp.option_G:
                c_uri = self.course_uri(ctp.course.course_id)
                og_uri = self.optional_group_uri(ctp.option_G.id)

                # OWX hasOptionalGroup: Domain CTP, Range OptionalGroup.
                # Your request is Course -> OptionalGroup. This is a "shortcut".
                # For this direct link, you'd need a custom predicate:
                # e.g. <owl:ObjectProperty rdf:about="&myonto;courseOfferedInOptionalGroup">
                #        <rdfs:domain rdf:resource="&myonto;Course"/>
                #        <rdfs:range rdf:resource="&myonto;OptionalGroup"/>
                #      </owl:ObjectProperty>
                g.add((c_uri, MYONTO.courseOfferedInOptionalGroup, og_uri))  # Custom predicate

                # The OWX-aligned relation is:
                ctp_i_uri = self.course_training_program_uri(ctp.pk)
                g.add((ctp_i_uri, MYONTO.hasOptionalGroup, og_uri))  # This matches OWX

    def populate_group_credit_relations(self, g):
        self.stdout.write("Populating OptionalGroup-Credit relations...")
        # IDGroup hasCredit Credit (min_credits for OptionalGroup)
        for og in OptionalGroup.objects.all():
            if og.min_credits is not None:
                og_uri = self.optional_group_uri(og.id)
                # OWX: hasCredit Domain: Course. This is for course credits.
                # For OptionalGroup's min_credits, you need a specific predicate.
                # e.g. <owl:DataProperty rdf:about="&myonto;hasMinimumCredits">
                #        <rdfs:domain rdf:resource="&myonto;OptionalGroup"/>
                #        <rdfs:range rdf:resource="&xsd;integer"/>
                #      </owl:DataProperty>
                g.add((og_uri, MYONTO.hasMinimumCredits,
                       Literal(og.min_credits, datatype=XSD.integer)))  # Custom predicate