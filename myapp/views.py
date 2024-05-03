import asyncio
import datetime
import random
from enum import Enum

from django.contrib.auth.models import User, Group
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse

from .models import MethodBook, Author
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test


def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


def getAllBooks():
    return MethodBook.objects.all()


class Status(Enum):
    Progress = "In progress"
    Submitted = "Submitted to publisher"
    Published = "Published"

    def get_status(text: str):
        match text:
            case Status.Progress.value:
                return Status.Progress
            case Status.Submitted.value:
                return Status.Submitted
            case Status.Published.value:
                return Status.Published
            case _:
                return Status.Progress


class TypeOfWork(Enum):
    Method = "Методические указания"
    Science = "Научная статья"


def createMethodBook(Institute,
                     Type: TypeOfWork,
                     Title: str,
                     link: str,
                     Dekanat):
    book = MethodBook(
        university=Dekanat,
        institute=Institute,
        type_of_work=Type.value,
        name_of_work=Title,
        link=link,
        date_publish=datetime.date.today())
    book.save()
    return book


def addAuthorToWork(work, author):
    work.authors.add(author)


def getAllAuthors():
    return Author.objects.all()


def getAuthorsForWork(work):
    return work.authors.all()


def getAllAuthorsForAllWorks(works):
    return list(map(lambda work: work.authors.all(), works))


def getAuthorByUser(user):
    return Author.objects.get(user=user)


def getAuthorByID(id):
    return Author.objects.get(id=id)


def getAllBooksByAuthor(author):
    return author.method_books.all()


def getUserID(request):
    return request.GET.get("userid")


def getUser(request):
    return request.user


def Login(request):
    if request.method == 'POST':
        username = request.POST.get('Login')
        password = request.POST.get('Password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(Main)

    return render(request, 'myapp/LoginBS.html')


def Registration(request):
    return render(request, 'myapp/Auth/Login.html')


@login_required
def Main(request):
    books_authors = []
    books = getAllBooksByAuthor(getAuthorByUser(getUser(request)))
    for work in books:
        books_authors.append(getAuthorsForWork(work))

    books = list(books)
    books.reverse()
    books_authors.reverse()

    a = zip(books, books_authors)
    context = {
        "author": getAuthorByUser(getUser(request)),
        "books": zip(books, books_authors)
        # "books_authors": books_authors
    }
    return render(request, 'myapp/MainBS.html', context)


@login_required
def Plan(request):
    if request.method == 'POST':
        typeWork = TypeOfWork.Method
        if request.POST.get('book') == "science":
            typeWork = typeWork.Science

        work = createMethodBook(Institute=request.POST.get('Cafedra'),
                                Type=typeWork,
                                Title=request.POST.get('Title'),
                                link=request.POST.get('Link'),
                                Dekanat=request.POST.get('Dekanat'))

        addAuthorToWork(work, getAuthorByUser(getUser(request)))
        for author in request.POST.get('Authors').split(","):
            fio = str(author).split(" ")

            model_author = list()
            if len(fio) == 1:
                model_author = list(Author.objects.filter(last_name__exact=fio[0]))
            elif len(fio) == 2:
                model_author = list(Author.objects.filter(last_name__exact=fio[0], first_name__exact=fio[1]))

            if len(model_author) > 0:
                addAuthorToWork(work, model_author[0])

        # MethodBook.objects.filter(title__icontains=find)
        return redirect('Main')

    allBooks = getAllBooksByAuthor(getAuthorByUser(getUser(request)))
    allAuthors = getAllAuthorsForAllWorks(allBooks)

    context = {
        "data": zip(allBooks, allAuthors),
    }
    return render(request, 'myapp/Worker.html', context)


@login_required
# @user_passes_test(lambda u: in_group(u, 'Group Name'))
def PlanRegister(request):
    return render(request, 'myapp/PlanCreateBS.html')


def About(request):
    if getUserID(request) is not None:
        author = getAuthorByID(getUserID(request))

        books = getAllBooksByAuthor(author)
        authors = getAllAuthorsForAllWorks(books)

        context = {
            "Author": author,
            "data": zip(books, authors),
        }
        return render(request, 'myapp/About.html', context=context)

    user = getUser(request)
    if user is not None:
        author = getAuthorByUser(user)
        books = getAllBooksByAuthor(getAuthorByUser(user))
        authors = getAllAuthorsForAllWorks(books)
        context = {
            "Author": author,
            "data": zip(books, authors),
        }
        return render(request, 'myapp/About.html', context=context)

    return render(request, 'myapp/About.html')


# ?userid=1

@login_required
def Logout(request):
    logout(request)
    return redirect('Login')


def Library(request):
    books = getAllBooks()
    authors = getAllAuthorsForAllWorks(books)
    context = {
        "data": zip(books, authors),
    }
    return render(request, 'myapp/LibraryBS.html', context)


def Project(request):
    id = request.GET.get("id")
    approve = request.GET.get("approve")

    book = MethodBook.objects.get(id=int(id))
    if approve == "yes":
        book.agreement_author_id = getAuthorByUser(getUser(request)).id
        book.agreement_date = datetime.date.today()
    elif approve == "no":
        book.agreement_author_id = getAuthorByUser(getUser(request)).id
    book.save()

    authors = getAuthorsForWork(book)

    context = {
        "work": book,
        "authors": authors,
        "user": getAuthorByUser(getUser(request))
    }
    return render(request, 'myapp/ProjectBS.html', context)


from django.db.models.functions import Lower


def FindWork(request):
    find = request.GET.get("find").upper()
    books = MethodBook.objects.filter(title__icontains=find)
    authors = getAllAuthorsForAllWorks(books)
    # Вывод найденных объектов
    book_list = []
    for book, authors in zip(books, authors):
        author_list = []
        author_id_list = []
        for author in authors:
            author_list.append(f"{author.last_name} {author.first_name} {author.middle_name}")
            author_id_list.append(author.id)

        work = {"number": book.number,
                "title": book.title,
                "date": book.date,
                "status": book.status,
                "authors": author_list,
                "authors_id": author_id_list
                }
        print("f")
        book_list.append(work)
    return JsonResponse({"data": book_list})


# http://127.0.0.1:8000/myapp/Edit?id=11&type=method&title=ЦИФРОВАЯ%20ТРАНСФОРМАЦИЯ%20МИРА&status=0
def EditWork(request):
    type_work = request.GET.get("type")
    id = request.GET.get("id")
    work = None

    if type_work == "method":
        work: MethodBook = MethodBook.objects.get(id=int(id))

    if work is None:
        return HttpResponse(status=404)

    # Поиск авторов, если автора нет в работе, запрет на редактирование.
    list_authors: list = getAuthorsForWork(work)
    if getAuthorByUser(getUser(request)) not in list_authors and \
            getUser(request).groups.filter(name='Editors').exists() is False:
        return HttpResponse(status=403)

    if Status.get_status(work.status) is not Status.Progress and \
            getUser(request).groups.filter(name='Editors').exists() is False:
        return HttpResponse(status=403)

    if request.GET.get("title") is not None:
        work.title = str(request.GET.get("title")).upper()

    if request.GET.get("number") is not None and type_work == "method":
        work.number = int(request.GET.get("number"))

    if request.GET.get("status") is not None and \
            getUser(request).groups.filter(name='Editors').exists() is True:

        match int(request.GET.get("status")):
            case 0:
                status_word = Status.Progress.value
            case 1:
                status_word = Status.Submitted.value
            case 2:
                status_word = Status.Published.value
            case _:
                status_word = Status.Progress.value
        work.status = status_word

    # print(request.user.groups.all())
    work.save()
    return HttpResponse("", status=200)


def SSE(request):
    return render(request, 'myapp/SSE.html')


async def sse_stream(request):
    """
    Sends server-sent events to the client.
    """

    async def event_stream():
        emojis = ["🚀", "🐎", "🌅", "🦾", "🍇"]
        i = 0
        while True:
            yield f'data: {random.choice(emojis)} {i}\n\n'
            i += 1
            await asyncio.sleep(1)

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def WS(request):
    return render(request, 'myapp/WS.html')
