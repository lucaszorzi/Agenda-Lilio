from agendalilio import settings
import urllib
import secrets

import datefinder
import json
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from httplib2 import Http

# MODELS
from agendalilio.models import token_google_user
from agendalilio.models import Event

from django.views.decorators.csrf import csrf_protect

import datetime


@login_required(login_url='/accounts/login/')
def google_login(request):
    token_request_uri = "https://accounts.google.com/o/oauth2/auth"
    response_type = "code"
    client_id = "545631998022-kbtutc6frk6dalrkpo7ehrsb1dsknman.apps.googleusercontent.com"
    if settings.BD_USE == 1:
        redirect_uri = "https://localhost:8000/googlecallback"
    else:
        redirect_uri = "http://localhost:8000/googlecallback"
    scope = "https://www.googleapis.com/auth/calendar"
    url = "{token_request_uri}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}".format(
        token_request_uri=token_request_uri,
        response_type=response_type,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope)

    return HttpResponseRedirect(url)


def google_authenticate(request):
    parser = Http()
    login_failed_url = '/'
    if 'error' in request.GET or 'code' not in request.GET:
        return HttpResponseRedirect('{loginfailed}'.format(loginfailed=login_failed_url))

    access_token_uri = 'https://accounts.google.com/o/oauth2/token'
    if settings.BD_USE == 1:
        redirect_uri = "https://localhost:8000/googlecallback"
    else:
        redirect_uri = "http://localhost:8000/googlecallback"
    params = urllib.parse.urlencode({
        'code': request.GET['code'],
        'redirect_uri': redirect_uri,
        'client_id': '545631998022-kbtutc6frk6dalrkpo7ehrsb1dsknman.apps.googleusercontent.com',
        'client_secret': 'wNwrbn8B5uilN3_KTdTDxyts',
        'grant_type': 'authorization_code'
    })
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    resp, content = parser.request(access_token_uri, method='POST', body=params, headers=headers)
    token_data = json.loads(content)

    try:
        # adicionar campos de data de expire do token no banco para não fazer update sempre
        token_obj = token_google_user.objects.get(user_id=request.user.id)
        token_obj.token = token_data['access_token']
        token_obj.save()
    except:
        try:
            token_store = token_google_user.objects.create(token=token_data['access_token'],
                                                           user_id=request.user.id)
        except:
            return HttpResponseRedirect('/')

    resp, content = parser.request("https://www.googleapis.com/auth/calendar?access_token={accessToken}".format(
        accessToken=token_data['access_token']))

    return redirect('/event/all/')


@login_required(login_url='/accounts/login/')
def event_list_all(request):
    events = Event.objects.filter(start_datetime__gt=datetime.datetime.now(), user=request.user)

    return render(request, 'agenda/event_list_all.html', {'events': events})


@login_required(login_url='/accounts/login/')
def event_create(request):
    return render(request, 'agenda/event_create.html')


@login_required(login_url='/accounts/login/')
@csrf_protect
def event_create_submit(request):
    if request.POST:
        start_date = request.POST['date']
        start_time = request.POST['time']
        name = request.POST['name']
        patients_name = request.POST['patients_name']
        email = request.POST['email']
        whatsapp = request.POST['whatsapp']
        phone = request.POST['phone']
        user = request.user

        start_date_str = datetime.datetime.strptime(start_date, "%d/%m/%Y")

        ## VALIDAÇÃO ##
        if start_date is None:
            messages.error(request, 'Preencha corretamente o campo "Data"')
        elif start_date_str < datetime.datetime.now():
            messages.error(request, 'Selecione uma data correta')
        elif start_time is None:
            messages.error(request, 'Preencha corretamente o campo "Horário"')
        elif name is None:
            messages.error(request, 'Preencha corretamente o campo "Nome"')
        # .
        # .
        # .
        else:
            summary = 'Consulta de ' + patients_name

            description = 'Nome do paciente: ' + patients_name + '\n' + 'Nome: ' + name + '\n' + 'Email: ' + email + '\n' + 'Whatsapp: ' + whatsapp + '\n' + 'Telefone: ' + phone + '\n' + '\n' + 'Data: ' + start_date + '\n' + 'Horário: ' + start_time

            duration = 1

            start_datetime = datetime.datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d") + ' ' + start_time

            matches = list(datefinder.find_dates(start_datetime))
            if len(matches):
                start_datetime = matches[0]
                end_datetime = start_datetime + datetime.timedelta(hours=duration)

            event = {
                'summary': summary,
                'location': '800 Howard St., San Francisco, CA 94103',
                'description': description,
                'start': {
                    'dateTime': start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                    'timeZone': 'America/Sao_Paulo',
                },
                'attendees': [
                    {'email': email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }

            token_obj = token_google_user.objects.get(user_id=request.user.id)

            url = "https://www.googleapis.com/calendar/v3/calendars/primary/events?access_token={accessToken}".format(
                accessToken=token_obj.token)
            headers = {'content-type': 'application/json'}
            resp, content = Http().request(url, method='POST', body=json.dumps(event), headers=headers)

            # content retorna todos os dados do evento em uma lista, tem que percorrer ela e ver se retornou o
            # id do evento, se sim, insere no banco, senão falha.

            event_data = json.loads(content)

            if event_data['id']:

                # Cria o evento no BD
                try:
                    event_create = Event.objects.create(name=name, patients_name=patients_name, email=email,
                                                        whatsapp=whatsapp, phone=phone, birth_date='2019-01-01',
                                                        description=description, start_datetime=start_datetime,
                                                        finish_datetime=end_datetime, google_event_id=event_data['id'],
                                                        user=user)
                    messages.success(request, 'Evento criado com sucesso!')
                    return redirect('/')
                except:
                    messages.error(request, 'Erro na criação do evento, tente novamente')
                    # return redirect('/event/delete/', id=event_data['id'])
            else:
                messages.error(request, 'Erro na criação do evento, tente novamente')
        return redirect('agenda:event_create')


@login_required(login_url='/accounts/login/')
def event_delete(request, id):
    event = Event.objects.get(id=id)

    if event.user == request.user:
        # deleta evento no DB
        try:
            event.delete()
        except:
            messages.success(request, 'Evento não pôde ser deletado, tente novamente!')
            return HttpResponseRedirect('/')

        # deleta evento no Google
        token_obj = token_google_user.objects.get(user_id=request.user.id)
        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}?access_token={accessToken}".format(
            event_id=event.google_event_id, accessToken=token_obj.token)
        resp, content = Http().request(url, method='DELETE')

        messages.success(request, 'Evento deletado com sucesso!')
    else:
        messages.error(request, 'Você não tem permissão para deletar este evento!')

    return redirect('/')


@login_required(login_url='/accounts/login/')
def index(request):
    token_obj = token_google_user.objects.get(user_id=request.user.id)

    events_list = Http().request(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events?access_token={accessToken}".format(
            accessToken=token_obj.token))

    # events = events_list.get('items', [])

    return render(request, 'agenda/index.html', {'events': events_list})
