
from odoo import models, fields, api


class EducationExamResultsNew(models.Model):
    _name = 'education.exam.results.new'
    _description = "this table contains student Wise exam results"

    name = fields.Char(string='Name' ,related="result_id.name" , store=True)
    result_id=fields.Many2one("education.exam.results","result_id")             #relation to the result table
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    section_id = fields.Many2one('education.class.section', string='Section',related="student_history.section",store=True)
    student_id = fields.Many2one('education.student', string='Student')
    student_history=fields.Many2one('education.class.history',"Student History",compute="get_student_history",store=True)
    student_name = fields.Char(string='Student')
    subject_line = fields.One2many('results.subject.line.new', 'result_id', string='Subjects')
    general_subject_line = fields.One2many('results.subject.line.new', 'general_for', string='General Subjects')
    optional_subject_line = fields.One2many('results.subject.line.new', 'optional_for', string='optional Subjects')
    extra_subject_line = fields.One2many('results.subject.line.new', 'extra_for', string='extra Subjects')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year',
                                    related='division_id.academic_year_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    total_pass_mark = fields.Float(string='Total Pass Mark')
    total_max_mark = fields.Float(string='Total Max Mark')

    general_full_mark=fields.Float("Full Mark")
    general_obtained=fields.Integer("General_total")
    general_count=fields.Integer("General Count")
    general_row_count=fields.Integer("General Count")
    general_fail_count = fields.Integer("Genera Fail")
    general_gp=fields.Float('general LG')
    general_gpa = fields.Float("general GPA",compute="get_general_gpa",store=True)

    extra_Full=fields.Integer("extra Full mark")
    extra_obtained=fields.Integer("extra total")
    extra_count=fields.Integer("extra Count")
    extra_row_count=fields.Integer("extra Row Count")
    extra_fail_count=fields.Integer("Extra Fail")
    extra_gp=fields.Float('Extra LG')
    extra_gpa = fields.Float("Extra GPA")

    optional_Full=fields.Integer("Optional full")
    optional_obtained=fields.Integer("Optional obtained")
    optional_count=fields.Integer("optional Count")
    optional_row_count=fields.Integer("optional Row Count")
    optional_fail_count=fields.Integer("optional Fail Count")
    optional_gp=fields.Float('Optional LG')
    optional_gpa = fields.Char("Optional GPA")
    optional_gpa_above_2 = fields.Float("Optional GPA Above 2")
    optional_obtained_above_40_perc=fields.Integer("Aditional marks from optionals")

    net_obtained = fields.Integer(string='Total Marks Scored')
    net_pass = fields.Boolean(string='Overall Pass/Fail')
    net_lg=fields.Char("Letter Grade")
    net_gp = fields.Float("Net GP")
    net_gpa=fields.Float("GPA")

    working_days=fields.Integer('Working Days')
    attendance=fields.Integer('Attendance')
    percentage_of_attendance=fields.Float("Percentage of Attendance")
    behavior=fields.Char("Behavior")
    sports=fields.Char("Sports Program")
    uniform=fields.Char("Uniform")
    cultural=fields.Char("Caltural Activities")
    # state=fields.Selection([('draft',"Draft"),('done',"Done")],"State",default='draft')

    show_tut=fields.Boolean('Show Tutorial')
    show_subj=fields.Boolean('Show Subj')
    show_obj=fields.Boolean('Show Obj')
    show_prac=fields.Boolean('Show Prac')
    show_paper=fields.Boolean('Show Papers')
    result_type_count=fields.Integer("result type Count",compute="get_result_type_count")
    @api.depends('show_tut','show_subj','show_obj','show_prac')
    def get_result_type_count(self):
        for rec in self:
            res_type_count=0
            if rec.show_tut==True:
                res_type_count=res_type_count+1
            if rec.show_subj==True:
                res_type_count=res_type_count+1
            if rec.show_obj==True:
                res_type_count=res_type_count+1
            if rec.show_prac==True:
                res_type_count=res_type_count+1
            rec.result_type_count=res_type_count

    @api.depends('general_gp','general_count')
    def get_general_gpa(self):
        for rec in self:
            if rec.general_count>0:
                if rec.general_fail_count<1:
                    if rec.extra_fail_count < 1:
                        rec.general_gpa=rec.general_gp/rec.general_count
            if rec.optional_count>0:
                if rec.optional_fail_count<1:
                    rec.optional_gpa=rec.optional_gp/rec.optional_count
                    if rec.optional_gpa>2:
                        rec.optional_gpa_above_2=rec.optional_gpa-2

                    if rec.optional_gpa>0:
                        optional_40_perc=rec.optional_Full*100/40
                        rec.optional_obtained_above_40_perc=rec.optional_obtained-optional_40_perc
            rec.net_obtained=rec.general_obtained+rec.optional_obtained_above_40_perc
            if rec.general_count>0:
                rec.net_gpa=rec.general_gpa+(rec.optional_gpa_above_2/rec.general_count)
            if rec.extra_count>0:
                if rec.extra_fail_count<1:
                    rec.extra_gpa=rec.extra_gp/rec.extra_count


    @api.depends('student_id','class_id')
    def get_student_history(self):
        for rec in self:
            history = self.env['education.class.history'].search(
                [('student_id', '=', rec.student_id.id), ('academic_year_id', '=', rec.academic_year.id)])
            rec.student_history=history.id

    @api.multi
    def calculate_result(self,exams):
        for exam in exams:
            self.env['education.exam.results.new'].search([('exam_id','=',exam.id)]).unlink()

            results = self.env['education.exam.results'].search([('exam_id','=',exam.id)])
            for result in results:
                result_data={
                    "name": exam.name,
                    "exam_id": exam.id,
                    "student_id": result.student_id.id,
                    "result_id": result.id,
                    "academic_year": exam.academic_year.id,
                    "student_name": result.student_name,
                    "class_id": result.class_id.id
                }
                student_exam_obtained=0
                student_exam_passed=True

                newResult=self.create(result_data)
                subject_list = {}
                for paper in result.subject_line_ids:
                    subjectId=paper.subject_id.subject_id
                    if subjectId not in subject_list:
                        subject_data={
                            "subject_id":subjectId.id,
                            "result_id":newResult.id,

                        }
                        newSubject=self.env["results.subject.line.new"].create(subject_data)
                        subject_list[subjectId] = newSubject
                    else:
                        newSubject=subject_list[subjectId]
                    paper_data={
                        "subject_line": newSubject.id,
                        "paper_id": paper.subject_id.id,
                        "tut_obt": paper.tut_mark,
                        "subj_obt": paper.subj_mark,
                        "obj_obt": paper.obj_mark,
                        "prac_obt": paper.prac_mark,
                        "tut_pr": paper.tut_pr,  #pr for present/Absent data
                        "subj_pr": paper.subj_pr,
                        "obj_pr": paper.obj_pr,
                        "prac_pr": paper.prac_pr,
                    }
                    new_paper=self.env["results.paper.line"].create(paper_data)
                    ful_mark=0
                    Passed=True
                    obtained=0

                    if newResult.class_id.id==11: # here 11 is for class SSC
                        if new_paper.paper_id.prac_mark>0:
                            if new_paper.prac_pr==False:  #check Present
                                Passed = False
                            if new_paper.paper_id.prac_pass>new_paper.prac_obt:
                                Passed=False
                            obtained=obtained+new_paper.prac_obt
                            ful_mark=ful_mark+new_paper.paper_id.prac_mark
                            newSubject.prac_mark=newSubject.prac_mark+new_paper.paper_id.prac_mark
                            newSubject.prac_ob=newSubject.prac_ob+new_paper.prac_obt


                        if new_paper.paper_id.subj_mark>0:
                            if new_paper.subj_pr==False:  #check Present
                                Passed = False
                            if new_paper.paper_id.subj_pass>new_paper.subj_obt:
                                Passed=False
                            obtained=obtained+new_paper.subj_obt
                            ful_mark = ful_mark + new_paper.paper_id.subj_mark
                            newSubject.subj_mark = newSubject.subj_mark + new_paper.paper_id.subj_mark
                            newSubject.subj_ob = newSubject.subj_ob + new_paper.subj_obt
                        if new_paper.paper_id.obj_mark>0:
                            if new_paper.obj_pr==False:  #check Present
                                Passed = False
                            if new_paper.paper_id.obj_pass>new_paper.obj_obt:
                                Passed=False
                            obtained=obtained+new_paper.obj_obt
                            ful_mark = ful_mark + new_paper.paper_id.obj_mark
                            newSubject.obj_mark = newSubject.obj_mark + new_paper.paper_id.obj_mark
                            newSubject.obj_ob = newSubject.obj_ob + new_paper.obj_obt
                        if new_paper.paper_id.tut_mark>0:
                            if new_paper.tut_pr==False:  #check Present
                                Passed = False
                            if new_paper.paper_id.tut_pass>new_paper.tut_obt:
                                Passed=False
                            obtained=obtained+new_paper.tut_obt
                            ful_mark = ful_mark + new_paper.paper_id.tut_mark
                            newSubject.tut_mark = newSubject.tut_mark + new_paper.paper_id.tut_mark
                            newSubject.tut_ob = newSubject.tut_ob + new_paper.tut_obt
                        if new_paper.paper_id.pass_mark > obtained:
                            Passed = False
                        new_paper.passed=Passed
                        new_paper.paper_obt=obtained
                        new_paper.paper_full=ful_mark
                        if Passed==True:
                            new_paper.gp=self.env['education.result.grading'].get_grade_point(new_paper.paper_id.total_mark,obtained)
                            grades = self.env['education.result.grading'].search([('score', '<=', new_paper.gp)],
                                                                                 limit=1, order='score DESC')
                            new_paper.lg= grades.result
                        else:
                            new_paper.gp=0
                            new_paper.lg="F"
            self.calculate_subjects_results(exam)
                # TODO edit students results Here
    @api.multi
    def calculate_subjects_results(self,exam):
        student_lines=self.search([('exam_id','=',exam.id)])
        for student in student_lines:
            student_compulsory_obtained=0
            compulsory_gp=0
            compulsory_count=0
            student_optional_obtained=0
            optional_gp=0
            optional_count=0

            student_extra_obtained=0
            extra_count=0
            extra_gp=0

            student_passed=True


            for subject in student.subject_line:
                paper_count=0
                passed=True
                fullmark=0
                optional=False
                extra=False
                obtained=0
                for paper in subject.paper_ids:
                    fullmark = fullmark + paper.paper_id.total_mark
                    obtained=obtained+paper.paper_obt
                    if paper.paper_id in student.student_history.optional_subjects:
                        optional_=True
                    elif paper.paper_id.evaluation_type=='extra':
                        extra=True

                    paper_count=paper_count+1
                    if paper.passed==False:
                        passed=False
                    if paper.paper_id.tut_mark>0:
                        student.show_tut=True
                    if paper.paper_id.subj_mark>0:
                        student.show_subj=True
                    if paper.paper_id.obj_mark>0:
                        student.show_obj=True
                    if paper.paper_id.prac_mark>0:
                        student.show_prac=True
                subject.max_mark=fullmark
                subject.mark_scored=obtained
               ########################################################
               #Start here to impliment the logic for all class pass fail rules
                #### rules for class SSC ,ID==11
                if student.student_history.class_id.class_id.id==11:  # 11 is id of class ssc
                    #### Rules for English , ID==2
                    if subject.subject_id.id==2: # rules for English
                        if subject.mark_scored<33 : #TODO implement subject.subject_id.pass_mark
                            passed=False
                    #### Rules for ICT , ID==6
                    elif subject.subject_id.id==6: # rules for English
                        if subject.mark_scored<17:  #TODO implement subject.subject_id.pass_mark
                            passed=False
                    else:
                        if subject.mark_scored<subject.pass_mark:
                            passed=False

                #end of pass fail rules
                ###############################################################
                if passed==True:
                    subject.grade_point=self.env['education.result.grading'].get_grade_point(fullmark,subject.mark_scored)
                    grades = self.env['education.result.grading'].search([('score', '<=', subject.grade_point)],
                                                                         limit=1, order='score DESC')
                    subject.letter_grade = grades.result
                else:
                    subject.grade_point=0
                    subject.letter_grade="F"
                if extra==True:
                    subject.extra_for=student.id
                    student.extra_row_count=student.extra_row_count+paper_count
                    student.extra_count=student.extra_count+1
                    student.extra_obtained=student.extra_obtained+subject.mark_scored
                    student.extra_gp=student.extra_gp+subject.grade_point
                    if passed==False:
                        student.extra_fail_count=student.extra_fail_count +1
                elif optional==True:
                    subject.optional_for=student.id
                    student.optional_count = student.optional_count + 1
                    student.optional_row_count = student.optional_row_count + paper_count
                    student.optional_obtained = student.optional_obtained + subject.mark_scored
                    student.optional_gp = student.optional_gp + subject.grade_point
                    if passed==False:
                        student.optional_fail_count = student.optional_fail_count + 1
                else:
                    subject.general_for=student.id
                    student.general_count = student.general_count + 1
                    student.general_row_count = student.general_row_count + paper_count
                    student.general_obtained = student.general_obtained + subject.mark_scored
                    student.general_gp = student.general_gp + subject.grade_point
                    if passed==False:
                        student.general_fail_count = student.general_fail_count + 1
                if paper_count>1:
                    student.show_paper=True
class ResultsSubjectLineNew(models.Model):
    _name = 'results.subject.line.new'
    name = fields.Char(string='Name',related='subject_id.name')
    result_id = fields.Many2one('education.exam.results.new', string='Result Id', ondelete="cascade")
    general_for = fields.Many2one('education.exam.results.new', string='General', ondelete="cascade")
    optional_for = fields.Many2one('education.exam.results.new', string='optional', ondelete="cascade")
    extra_for = fields.Many2one('education.exam.results.new', string='Extra', ondelete="cascade")
    pass_rule_id=fields.Many2one('exam.subject.pass.rules',"Pass Rule")
    subject_id = fields.Many2one('education.subject', string='Subject')
    paper_ids=fields.One2many('results.paper.line','subject_line','Papers')
    tut_mark = fields.Integer(string='Tutorial')
    tut_pass = fields.Integer(string='Pass')
    subj_mark = fields.Integer(string='Subjective')
    subj_pass = fields.Integer(string='pass')
    obj_mark = fields.Integer(string='Objective')
    obj_pass = fields.Integer(string='pass')
    prac_mark = fields.Integer(string='Practical')
    prac_pass = fields.Integer(string='pass')
    tut_ob = fields.Integer(string='Tutorial')
    subj_ob = fields.Integer(string='Subjective')
    obj_ob = fields.Integer(string='Objective')
    prac_ob = fields.Integer(string='Practical')
    letter_grade=fields.Char('Grade')
    grade_point=fields.Float('GP')
    max_mark = fields.Float(string='Max Mark')
    pass_mark = fields.Float(string='Pass Mark')
    mark_scored = fields.Float(string='Mark Scored')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

class result_paper_line(models.Model):
    _name = 'results.paper.line'
    subject_line=fields.Many2one('results.subject.line.new',ondelete="cascade")
    pass_rule_id=fields.Many2one("exam.paper.pass.rules","pass Rule")
    paper_id=fields.Many2one("education.syllabus","Paper",related="pass_rule_id.paper_id")
    paper_name=fields.Char("Name", related="paper_id.paper")
    tut_mark=fields.Float("Tutorial",related="pass_rule_id.tut_mark")
    tut_pass=fields.Float("Pass",related="pass_rule_id.tut_pass")
    subj_mark=fields.Float("Subjective",related="pass_rule_id.subj_mark")
    subj_pass=fields.Float("Pass",related="pass_rule_id.subj_pass")
    obj_mark=fields.Float("Objective",related="pass_rule_id.obj_mark")
    obj_pass=fields.Float("Pass",related="pass_rule_id.obj_pass")
    prac_mark=fields.Float("Practical",related="pass_rule_id.prac_mark")
    prac_pass=fields.Float("Pass",related="pass_rule_id.prac_pass")
    total_mark=fields.Float("Total",related="pass_rule_id.total_mark")
    pass_mark=fields.Float("Pass",related="pass_rule_id.total_pass")
    tut_obt = fields.Float(string='Tutorial')
    subj_obt = fields.Float(string='Subjective')
    obj_obt = fields.Float(string='Objective')
    prac_obt = fields.Float(string='Practical')
    prac_pr = fields.Boolean(string='P',default=False)
    subj_pr = fields.Boolean(string='P',default=False)
    obj_pr = fields.Boolean(string='P',default=False)
    tut_pr = fields.Boolean(string='P',default=False)
    paper_obt=fields.Float("Paper obtained Mark")
    passed=fields.Boolean("Passed?")
    lg=fields.Char("letter Grade")
    gp=fields.Float("grade Point")