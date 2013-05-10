# -*- coding: utf-8 -*-
"""
    vyakarana.anga
    ~~~~~~~~~~~~~~

    Rules that apply specifically to an aṅga. Almost all such rules are
    within the domain of 6.4.1:

        6.4.1 aṅgasya

    which holds from the beginning of 6.4 to the end of 7.4. Of these
    rules, however, the ones from 7.4.58 onward apply specifically to
    the abhyāsa of some aṅga, as opposed to the aṅga itself.

    Some of the rules contained in this section apply in contexts where
    only a dhātu would make sense. But since a dhātu is a type of aṅga,
    there's no harm in matching on an aṅga generally.

    :license: MIT and BSD
"""

import gana
from classes import Sounds, Sound, Upadesha as U
from decorators import *


@require('dvirvacana')
@once('anga_adesha')
def adesha(state):
    i, dhatu = state.find('dhatu')
    value = dhatu.value
    next = state[i+1]

    # 6.1.16 vacisvapiyajAdInAM kiti
    # 6.1.17 grahi... Giti ca
    vac_condition = 'k' in next.it and value in gana.VAC
    grah_condition = value in gana.GRAH and next.any_it('k', 'N')
    if vac_condition or grah_condition:
        dhatu = dhatu.samprasarana()
        yield state.swap(i, dhatu)

    # 7.2.115 aco `Jniti (vrddhi)
    # 7.2.116 ata upadhAyAH
    elif next.any_it('Y', 'R'):
        if dhatu.ac or dhatu.upadha().value == 'a':
            dhatu = dhatu.vrddhi()
        else:
            dhatu = dhatu.guna()

        yield state.swap(i, dhatu)

    # 7.3.84 sArvadhAtukArdhadhAtukayoH
    elif next.any_samjna('sarvadhatuka', 'ardhadhatuka'):
        # 1.1.5 kGiti ca
        if next.any_it('k', 'N'):
            yield state
        else:
            dhatu = dhatu.guna()
            yield state.swap(i, dhatu)

    else:
        yield state


@once('rt')
def rt(state):
    i, anga = state.find('anga')
    p = state[i+1]
    if 'li~w' in p.lakshana:
        # 7.4.10 Rtaz ca saMyogAder guNaH
        _10 = anga.samyogadi and anga.ends_in('ft')
        # 7.4.10 RcchatyRRtAm
        _11 = anga.clean == 'f' or anga.ends_in('Ft')

        if _10 or _11:
            yield state.swap(i, anga.guna())


@once('anga_aci')
def aci(state):
    """
    Apply rules conditioned by a following vowel.

    This rule must not apply to terms that haven't gone through the
    vowel strengthening rules. Otherwise, we could get results like:

        tu + stu + a -> tu + stuv + a -> tuzwova

    when what we desire is:

        tu + stu + a -> tu + stO + a -> tuzwAva

    :param state:
    """
    i, anga = state.find('anga')
    p = state[i+1]

    if not anga.value:
        return

    f = anga.antya().value
    s = p.adi()

    if not s.ac:
        return

    # 6.4.88 bhuvo vuk luGliToH
    if anga.clean == 'BU':
        if anga.parts[-1].raw == 'vu~k':
            return
        else:
            anga = anga.tasya(U('vu~k'))
            yield state.swap(i, anga)

    elif f in Sounds('i u'):
        # 6.4.77 aci znudhAtubhruvAM yvor iyaGuvaGau
        # TODO: other categories
        _77 = 'dhatu' in anga.samjna

        # 6.4.78 abhyAsasyAsavarNe
        _78 = 'abhyasa' in anga.samjna and Sound(f).asavarna(s.value)
        if _77 or _78:
            if f in Sounds('i'):
                anga = anga.tasya(U('iya~N'))
            else:
                anga = anga.tasya(U('uva~N'))

            yield state.swap(i, anga)


@once('ac_adesha')
def ac_adesha(state):
    """
    Perform substitutions on the anga. These substitutions can occur
    after dvirvacana has been attempted.

    :param state:
    """

    # 1.1.59 dvirvacane 'ci
    # If dvirvacana has not been attempted, don't make any (root)
    # substitutions. Otherwise, we could get results like:
    #
    #     sTA + iTa -> sT + iTa -> t + sT + iTa -> tsTita
    #     gam + iva -> gm + iva -> j + gm + iva -> jgmiva
    #
    # when what we desire is:
    #
    #     sTA + iTa -> ta + sTA + iTa -> ta + sT + iTa -> tasTita
    #     gam + iva -> ja + gam + iva -> ja + gm + iva -> jagmiva
    if 'dvirvacana' not in state.ops:
        return

    i, anga = state.find('anga')
    tin = state[-1]

    # 6.4.64 Ato lopa iTi ca
    if anga.antya().value == 'A':
        if 'iw' in tin.parts[0].lakshana or 'k' in tin.it:
            anga = anga.antya('')
            yield state.swap(i, anga)
            return

    # 6.4.98 gamahanajanakhanaghasAM lopaH kGityanaGi
    # TODO: aG
    gam_adi = set('gam han jan Kan Gas'.split())
    if anga.value in gam_adi and ('k' in tin.it or 'N' in tin.it):
        anga = anga.upadha('')
        yield state.swap(i, anga)

    else:
        for s in lit_a_to_e(state):
            yield s


# @match('anga', 'pratyaya')
# def ku(anga, pratyaya):
#     """Apply rules that perform 'ku' substitutions.

#     Specifically, these rules are 7.3.52 - 7.3.69

#     :param abhyasa:
#     :param anga:
#     """

#     # 7.3.52 cajoH ku ghiNyatoH
#     # 7.3.53 nyaGkvAdInAM ca
#     # 7.3.54 ho hanter JNinneSu
#     # 7.3.55 abhyAsAc ca

#     # 7.3.56 her acaGi
#     if anga.clean == 'hi':


#     elif pratyaya.any('san', 'li~w'):

#         # 7.3.57 sanliTor jeH
#         if anga.clean == 'ji':

#         # 7.3.58 vibhASA ceH
#         elif anga.clean == 'ci':

#     return


def lit_a_to_e(state):
    """Applies rules that cause ed-ādeśa and abhyāsa-lopa.

    Specifically, these rules are 6.4.120 - 6.4.126.

    :param state: some State
    """
    i, abhyasa = state.find('abhyasa')
    j, anga = state.find('anga')
    # The right context of `anga`. This is usually a pratyaya.
    p = state[j+1]
    # True, False, or 'optional'. Crude, but it works.
    status = False

    liti = 'li~w' in p.lakshana
    # e.g. 'pac', 'man', 'ram', but not 'syand', 'grah'
    at_ekahal_madhya = (anga.upadha().value == 'a' and len(anga.value) == 3)
    # e.g. 'pac' (pa-pac), 'ram' (ra-ram), but not 'gam' (ja-gam)
    anadesha_adi = (abhyasa.value[0] == anga.value[0])

    if liti:
        # 'kGiti' is inherited from 6.4.98.
        kniti = 'k' in p.it or 'N' in p.it

        # 6.4.121 thali ca seTi
        thali_seti =  p.value == 'iTa'

        # This substitution is valid only in these two conditions.
        if not (kniti or thali_seti):
            return

        # 6.4.120 ata ekahalmadhye 'nAdezAder liTi
        if at_ekahal_madhya and anadesha_adi:
            status = True

        # 6.4.122 tRRphalabhajatrapaz ca
        if anga.clean in ('tF', 'Pal', 'Baj', 'trap'):
            status = True

        # 6.4.123 rAdho hiMsAyAm
        elif anga.clean == 'rAD':
            status = 'optional'

        # 6.4.124 vA jRRbhramutrasAm
        elif anga.clean in ('jF', 'Bram', 'tras'):
            status = 'optional'

        # 6.4.125 phaNAM ca saptAnAm
        elif anga.clean in gana.PHAN:
            status = 'optional'

        # 6.4.126 na zasadadavAdiguNAnAm
        # TODO: guna
        vadi = anga.adi().value == 'v'
        if anga.clean in ('Sas', 'dad') or vadi:
            status = False

    if status in (True, 'optional'):
        yield state.swap(i, abhyasa.lopa()).swap(j, anga.al_tasya('a', 'et'))

    if status in (False, 'optional'):
        yield state
