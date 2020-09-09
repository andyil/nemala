from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse, JsonResponse
from .models import Document, Answer
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth import logout
from django.db.models import Q, Count

from datetime import datetime, timedelta, timezone

the_tz = timezone(timedelta(hours=3))

PAGE_SIZE=100


from time import strftime, gmtime

import json

def is_boss(request):
    return request.user.is_authenticated and request.user.is_active and request.user.groups.filter(name='bosses').exists()

def home(request):
    template = loader.get_template('poorslaves/home.html')
    return HttpResponse(template.render({}, request))


def get_hint(document):
    hint = ""
    import re
    if hasattr(document, 'metadata'):
        metadata = json.loads(document.metadata)
        case_id = metadata['case_id'].replace('""', '"')
        case_id = re.sub('^["]', "", case_id)
        case_id = re.sub('["][ ]', " ", case_id)
        name = metadata['name']
        hint = '{case_id} {name}'.format(case_id=case_id, name=name)
    return hint


def random(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/admin/login", request.path))

    if is_boss(request):
        if not request.session.get('already_seen', False):
            request.session['already_seen'] = True
            return redirect('console')

    template = loader.get_template('poorslaves/random.html')

    today = datetime.now().date()
    start = today - timedelta(days=today.weekday())
    completed = Answer.objects.filter(accepted=True, user=request.user.username, created__gte=start).count()
    ten_min_ago = datetime.now(the_tz) - timedelta(minutes=15)
    documents_query =Document.objects.filter(answers=0)
    documents_query = documents_query.filter(
                Q(last_shown__lt=ten_min_ago) | Q(last_shown__isnull=True)
            ).order_by("views")
    available_documents = len(documents_query)
    if available_documents == 0:
        return HttpResponse(template.render({'completed': completed}, request))

    document = documents_query[0]
    document.views += 1
    document.last_shown = datetime.now(the_tz)
    document.save()
    hint = get_hint(document)

    questions = []
    context = {
        'hint': hint,
        'document': document,
        'questions': questions,
        'request': request,
        'completed': completed
    }
    return HttpResponse(template.render(context, request))

def my_logout(request):
    logout(request)
    return redirect('/')

def accept_answer(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    m = {}

    form = request.POST
    answer = {}
    for k, v in form.items():
        if k.endswith("-1"):
            newk = k.replace("-1", "court")
        elif '-' in k:
            parts = k.split("-")
            newk = "%s-%s" % (parts[0], (int(parts[1])-1))
        else:
            continue
        if "issue" in k:
            answer[newk] = ",".join(form.getlist(k))
        else:
            answer[newk] = v

    answer['meta'] = {'username': request.user.username, 'time':  strftime("%Y-%m-%d %H:%M:%S %z", gmtime())}
    document_id = request.POST["document"]
    document = Document.objects.get(id=document_id)
    document.answers += 1
    document.save()
    a = Answer(choice_text =json.dumps(answer), document=document)
    a.user = request.user.username
    a.accepted = True
    a.created = datetime.now(the_tz)
    a.save()
    return redirect('random')


def show_answers_excel(request):
    if not is_boss(request):
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    answers = Answer.objects.filter(Q(accepted=True) | Q(accepted__isnull=True)).all()
    column_names, answers_list = get_columns_and_answers(answers)
    from .excel import Excel
    e = Excel(column_names, answers_list)
    bytes = e.get()
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=answers.xlsx'
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.status_code = 200
    response.content = bytes
    return response


def column_sort_key(column_name):
    m = { 'id': -5, 'Document': -4,   'person': -3, 'created': -2.5,  'casename': -2,   'url': -1, 'court': 0}
    if column_name in m:
        return m[column_name]
    if 'court' in column_name:
        return 0.5
    if '-' in column_name:
        number = column_name.split('-')[1]
        if number.isnumeric():
            return int(number)
    return 100

def get_columns_and_answers(answers):
    column_names = ['id', _("Document"), 'person', 'created', 'casename', 'url']
    for answer in answers:
        text = answer.choice_text
        j = json.loads(text)
        for k in j.keys():
            if k.startswith("issue"):
                if '%s-1' % k not in column_names:
                    column_names.append('%s-1' % k)
                if '%s-2' % k not in column_names:
                    column_names.append('%s-2' % k)
            else:
                if k != "meta" and k not in column_names:
                    column_names.append(k)

    column_names = sorted(column_names, key=column_sort_key)

    answers_list = []
    for answer in answers:
        choice_text = answer.choice_text
        j = json.loads(choice_text)
        hint = get_hint(answer.document)
        row = [answer.id, answer.document.id, j['meta']['username'], answer.created, hint, answer.document.url]

        for column_name in column_names[6:]:
            if column_name.startswith("issue"):
                if column_name.endswith("-1"):
                    colname = "-".join(column_name.split("-")[:-1])
                    val = j.get(colname, "")
                    parts = val.split(',')
                    row.append(parts[0])
                    if len(parts) > 1:
                        row.append(parts[1])
                    else:
                        row.append('')
            else:
                val = j.get(column_name, "")
                row.append(val)

        answers_list.append(row)
    return column_names, answers_list

def add_search_filter(request, query):
    answer_search = request.GET.get('answer_search', '')
    if answer_search:
        query = query.filter(choice_text__contains=answer_search)
    document_search = request.GET.get('document_search', '')
    if document_search:
        documents = Document.objects.filter(metadata__contains=document_search)
        query = query.filter(document__in=documents)
    return query

def show_answers(request):
    if not is_boss(request):
        return redirect('%s?next=%s' % ("/admin/login", request.path))

    page_number = int(request.GET.get('page_number', 1))
    first = (page_number-1) * PAGE_SIZE
    last = first+PAGE_SIZE

    qry = Answer.objects.filter(Q(accepted=True) | Q(accepted__isnull=True))
    qry = add_search_filter(request, qry)
    total = qry.count()

    answers_query = Answer.objects.order_by("-created")
    answers_query = add_search_filter(request, answers_query)
    answers = answers_query.all()[first:last]
    column_names, answers_list = get_columns_and_answers(answers)
    template = loader.get_template('poorslaves/show_answers.html')
    context = {
        'column_names': column_names,
        'answers_list': zip(answers, answers_list),
        'total': total,
        'first': first+1,
        'last': last,
        'next_page' : page_number+1,
        'previous_page': page_number-1
    }
    return HttpResponse(template.render(context, request))



def admin_console(request):
    if not is_boss(request):
        return redirect('%s?next=%s' % ("/admin/login", request.path))
    return open_console(request)

def open_console(request):
    documents_count = Document.objects.count()
    solved = Document.objects.filter(answers__gt=0).count()
    repeated = Answer.objects.values('document_id').annotate(dcount=Count('document_id')).filter(dcount__gt=1).count()
    to_solve = Document.objects.filter(answers=0).count()
    week_ago = datetime.now(the_tz).date() - timedelta(days=7)

    last_week  =Answer.objects.filter(Q(accepted=True) | Q(accepted__isnull=True)).filter(created__gt=week_ago).count()

    day_start = datetime.now(the_tz).date()
    yesterday_start = day_start - timedelta(days=1)
    day_before_start = day_start - timedelta(days=2)

    today = Answer.objects.filter(Q(accepted=True) | Q(accepted__isnull=True)).\
            filter(created__gt= day_start).count()
    yesterday = Answer.objects.filter(Q(accepted=True) | Q(accepted__isnull=True)).\
            filter(created__gt= yesterday_start).filter(created__lt=day_start).count()
    day_before = Answer.objects.filter(Q(accepted=True) | Q(accepted__isnull=True)).\
        filter(created__gt= day_before_start).filter(created__lt=yesterday_start).count()

    if last_week == 0:
        finish_in = 99
    else:
        finish_in = to_solve / last_week
    context = {
        'documents_count': documents_count,
        'solved': solved, 'to_solve': to_solve,
        'repeated': repeated,
        'last_week': last_week,
        'today': today,
        'yesterday': yesterday,
        'day_before': day_before,
        'missing': to_solve,
        'remaining_weeks': int(finish_in)
    }

    template = loader.get_template('poorslaves/console.html')
    return HttpResponse(template.render(context, request))

def accept_reject(request):
    if not is_boss(request):
        raise "exc"

    id = request.POST["id"]
    checked = request.POST["checked"]

    answer = Answer.objects.filter(id=id)[0]
    answer.accepted = checked == 'true'
    if answer.accepted:
        answer.document.answers += 1
    else:
        answer.document.answers -= 1
    answer.save()
    answer.document.save()
    return JsonResponse({'success': True})