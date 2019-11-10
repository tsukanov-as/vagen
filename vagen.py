
from abc import ABC, abstractmethod

indent: int = 0

class Indent:

    def __init__(self, text):
        write(text)

    def __enter__(self):
        global indent
        indent += 1
        return indent

    def __exit__(self, exc_type, exc_value, traceback):
        global indent
        indent -= 1


_script: list = []


def script() -> str:
    """ Возвращает текст скрипта. """
    return "".join(_script)


def write(s):
    """ Добавляет в скрипт переданную строку с текущим отступом. """
    _script.append('\t' * indent)
    _script.append(s)
    _script.append('\n')


_forms = []


def push(form):
    """ Добавляет форму на стек форм. """
    _forms.append(form)


def pop(form):
    """ Снимает форму со стека форм. """
    assert form == _forms.pop()


def menu(section, item):
    write(f'And In the command interface I select "{section}" "{item}"')


class Form(ABC):

    def __init__(self, title: str):
        self.title: str = title

    def __enter__(self):
        """ Выполняется при входе в with """
        push(self)
        self.open()
        write(f'* in window "{self.title}"')
        global indent
        indent += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Выполняется при выходе из with """
        global indent
        indent -= 1
        pop(self)
        self.close()

    def open(self):
        """ Проверяет что форма открыта. """
        write(f'Then "{self.title}" window is opened')

    def close(self):
        """ Закрывает форму. """
        write(f'And I close "{self.title}" window')


class Field(ABC):

    def __init__(self, name, table=None):
        self.name: str = name
        self.table: Table = table


class TextField(Field):
    """ Текстовое поле. """

    def input(self, text, check=False):
        if self.table is None:
            write(f'And I input "{text}" text in the field named "{self.name}"')
            if check:
                self.check(text)
        else:
            write(f'And I input "{text}" text in the field named "{self.name}" of "{self.table.name}" table')
            if check:
                write(f'And I finish line editing in "{self.table.name}" table')
                write(f'Then the text of current cell of "{self.table.name}" table became equal to "{text}"')

    def check(self, text):
        write(f'Then the form attribute named "{self.name}" became equal to "{text}"')

    def choose(self, text):
        if self.table is None:
            write(f'And I click Choice button of the field named "{self.name}"')
        else:
            write(f'And I click choice button of the attribute named "{self.name}" in "{self.table.name}" table')

    def select(self, text):
        write(f'And I select "{text}" exact value from the drop-down list named "{self.name}"')


class RadioButton(Field):
    """ Переключатель. """

    def select(self, text):
        write(f'And I change the radio button named "{self.name}" value to "{text}"')


class CheckBox(Field):
    """ Флажок. """

    def enable(self):
        write(f'And I Set checkbox named "{self.name}"')

    def disable(self):
        write(f'And I Remove checkbox named "{self.name}"')


class Button(ABC):
    """ Обычная кнопка. """

    def __init__(self, name: str):
        self.name: str = name

    def click(self):
        write(f'And I click the button named "{self.name}"')


class Page(ABC):
    """ Страница. """

    def __init__(self, name: str):
        self.name: str = name

    def __enter__(self):
        """ Выполняется при входе в with """
        self.activate()
        write(f'* on page "{self.name}"')
        global indent
        indent += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Выполняется при выходе из with """
        global indent
        indent -= 1

    def activate(self):
        write(f'And I move to the tab named "{self.name}"')


class Table(ABC):
    """ Таблица. """

    def __init__(self, name: str):
        self.name: str = name

    def __enter__(self):
        """ Выполняется при входе в with """
        write(f'* in table "{self.name}"')
        global indent
        indent += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Выполняется при выходе из with """
        global indent
        indent -= 1

    def add(self):
        write(f'And in the table "PaymentDetails" I click the button named "{self.name}Add"')
        write(f'And I finish line editing in "{self.name}" table')

    def goto(self, target):
        write(f'And I go to line in "List" table')
        columns = []
        values = []
        for key in target:
            columns.append(key)
            values.append(target[key])
        global indent
        indent += 1
        write('|' + "|".join(columns) + '|')
        write('|' + "|".join(values) + '|')
        indent -= 1


class DocumentForm(Form):
    """ Форма документа. """

    Post = Button("FormPost")

    def post(self):
        write('* post document')
        global indent
        indent += 1
        self.Post.click()
        write('Then user message window does not contain messages')
        # write('And I save the value of "Number" field as "$$$$DocNum1$$$$"')


class ListForm(Form):
    """ Форма списка документов. """

    List = Table("List")  # можно переопределить в потомках если имя отличается

    Create = Button("FormCreate")

    def create(self):
        self.Create.click()

    def goto(self, target):
        self.List.goto(target)


class ChoiceForm(Form):
    """ Форма списка документов. """

    List = Table("List")  # можно переопределить в потомках если имя отличается

    Select = Button("FormSelect")

    def select(self):
        write(f'And I select current line in "{self.List.name}" table')
        pop(self)


    def goto(self, target):
        self.List.goto(target)

    def __exit__(self, exc_type, exc_value, traceback):
        """ Выполняется при выходе из with """
        global indent
        indent -= 1
        _forms[-1].open()
