from holidays.countries import Brazil

"""

Mais exemplos sobre a biblioteca em: https://python-holidays.readthedocs.io/en/latest/examples.html#add-years-to-an-existing-holiday-object

"""


class BancoCentralHolidays(Brazil):

    def _populate(self, year):
        super()._populate(year)
        
        # self._add_holiday_may_31("Corpus Christi")
        # self._add_corpus_christi_day("Corpus Christi")
        self._populate_optional_holidays()
        # Adicionar novos feriados opcionalmente.


