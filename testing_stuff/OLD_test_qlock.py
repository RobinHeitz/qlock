import pytest

from helper_funcs import translate_to_12h_clock_format, clock_words, next_hour
from pixel_definition import WD_IT_IS, WD_after, WD_before


class TestHelperFunctions():
    """This class tests helper functions. Not intended to already implement clock logic like which pixel should be displayed at a given time.
    Only test, whether these functions return the correct vals."""
    

    @pytest.mark.parametrize("input_hour, output_hour", [
        (0,1),
        (10,11),
        (11,12),
        (12,13),
        (22,23),
        (23,0),
    ])
    def test_next_hour(self, input_hour, output_hour):
        """Tests whether the function actually returns the right numbers."""
        assert output_hour == next_hour(input_hour)


    @pytest.mark.parametrize("hours, expected", [
    (0,0),
    (11,11),
    (12,12),
    (13,1),
    (23,11),
])
    def test_translate_to_12h_format(self, hours, expected):
        """Testing the 12h clock format transformation.
        
        If the arg is 13, we expect 1 to be returned. For 12 hours, 12 should be returned and 11 for an input of 23."""
        assert expected  == translate_to_12h_clock_format(hours)




    @pytest.mark.parametrize("minutes, contains_after", [
        (0,False),
        (4,False),
        (5,True),
        (9,True),
        (10,True),
        (11,True),
        (15,True),
        (16,True),
        (19,True),
        (20,True),
        (21,True),
        (25,False),
        (26,False),
        (29,False),
        (30,False),
        (34,False),
        (35,True),
        (39,True),
        (40,False),
        (41,False),
        (45,False),
        (46,False),
        (49,False),
        (50,False),
        (51,False),
        (59,False),

    ])
    def test_clock_word_after(self, minutes, contains_after):
        """Receive minutes [0, 59] as input and checks whether pixels are withing returned list."""
        pixels = clock_words(minutes)
        assert contains_after == all(item in pixels for item in WD_after)


    

    @pytest.mark.parametrize("minutes, contains_before", [
        (0,False),
        (5,False),
        (10,False),
        (15,False),
        (20,False),
        (24,False),
        (25,True),
        (29,True),
        (30, False),
        (35, False),
        (39, False),
        (40, True),
        (45, True),
        (50, True),
        (55, True),
        (59, True),
    ])
    def test_clock_word_before(self, minutes, contains_before):
        """Receives minutes [0,60) as input and checks whether pixels for the word 'before' are part of the output list."""
        pixels = clock_words(minutes)
        assert contains_before == all(item in pixels for item in WD_before)

    




        