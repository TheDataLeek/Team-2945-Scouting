#!/usr/bin/env python

import sys
import csv
import optparse
import time


def main():

    loggen = Log_File_Generation()
    loggen.log_clean()

    start_time = time.time()
    print 'Process started at ', start_time

    opts = get_opts()

    match_scores = collect(opts)
    print 'Data Collection Complete'

 #   print match_scores
    assert(match_scores != [])


    team_scores = match_consolidation(match_scores, opts)
    #print mean_scores

    Scoring = DataScoring()
    weighted_scores = Scoring.summation(team_scores, opts)
    print 'Data Scoring Complete'

    #print weighted_scores

    Latex = DataFormat(opts)
    Latex.latex_writer(weighted_scores, opts)
    print 'Latex Generation Complete'

    end_time = time.time()
    print 'Process Completed at ', end_time
    print 'Duration = ', end_time - start_time


def collect(opts):
    Collection = DataCollection()

    scores = []

    for number in range(1,2):
        filename = 'data' + str(number) + '.csv'
        in_file = open(filename, 'r')
        data = csv.reader(in_file, delimiter=',')
        for row in data:
            if Collection.data_assurance(row, opts):
                scores.append(row)
        in_file.close()
    sorted_scores = sorted(scores, key=lambda score : int(score[0]))
    if opts.visual == True:
        print 'Bad Row Count = ', Collection.bad_count
    return sorted_scores

class DataCollection:    # Turn into function

    def __init__(self):
        self.bad_count = 0

    def data_assurance(self, row, opts):
        loggen = Log_File_Generation()
        item_count = 0
        for item in row:
            item_count += 1
            if item_count not in [1,2,13]:
                try:
                    if int(item) > 10:
                        error = 'ERROR 1: Data issue, field range'
                        self.bad_count += 1
                        loggen.logfile.write(error + str(row) + '\n')
                        if opts.visual == True:
                            print error, row 
                        return False
                    elif int(item) < 1:
                        error = 'ERROR 2: Data issue, field range'
                        loggen.logfile.write(error + str(row) + '\n')
                        self.bad_count += 1
                        if opts.visual == True:
                            print error, row
                        return False
                except ValueError:
                    error = 'ERROR 3: Data issue, alpha-characters'
                    loggen.logfile.write(error + str(row) + '\n')
                    self.bad_count += 1
                    if opts.visual == True:
                        print error, row
                    return False
        if item_count != 13:
            error = 'ERROR 4: Data issue, too many fields'
            loggen.logfile.write(error + str(row) + '\n')
            self.bad_count += 1
            if opts.visual == True:
                print error, row
            return False
        elif item_count == 13:
            return True


def match_consolidation(scores, opts):
    ''' Gets raw input scores and returns a list that contains just 1 row
        per team with average scores.
    '''
    Average = DataAverage()
    sorted_teams = Average.seperator(scores, opts)
    consolidated_scores = Average.mean(sorted_teams, opts)
    assert(len(consolidated_scores[1]) == 12)
    if opts.visual == True:
        print consolidated_scores
    return consolidated_scores


class DataAverage:

    def seperator(self, scores, opts):
        ''' Restructures data by team:
            <example>
            and describe
        '''
        team_array   = []
        sorted_teams = []
        for item in scores:
            if team_array == []:
                team_array.append(item)
            elif item[0] == team_array[0][0]:
                team_array.append(item)
            else:
                sorted_teams.append(team_array)
                team_array = []
        sorted_teams.append(team_array)
        if opts.visual == True:
            print sorted_teams
        return sorted_teams

    def mean(self, sorted_teams, opts):
        ''' Returns one row per team with fields that are averages of inputs.
            Input description:  blahblah
            Output desc: blahfoobar
        '''
        mean_scores = []
        for team in sorted_teams:
            self.total_matches = len(team)
            self.y_count = 1.0
            self.n_count = 1.0
            mean_team = [team[0][0]]
            for field in range(2, 13):
                total = 0
                for match in team:
                    if field == 12:
                        self.win_ratio(match)
                    else:
                        weighted_field = self.weight_number(match, field, opts)
                        total += weighted_field
                if field == 12:
                    ratio = round(100 *(self.y_count / (self.y_count + self.n_count)), 2)
                    mean_team.append(ratio)
                else:
                    mean_team.append(total)
            if opts.visual == True:
                print mean_team
            mean_scores.append(mean_team)
        return mean_scores

    def win_ratio(self, match):
        if match[12].lower() in ['y', 'yes', 'tie']:
            self.y_count += 1.0
        elif match[12] in ['n', 'no']:
            self.n_count += 1.0

    def weight_number(self, match, field, opts):
        ''' For weighting a certain process needs to be done
            Find standard mean gap
            Find match range
            Find the percent increase per match
            Multiply match number by the percent increase by the percent
            Essentially want the middle (50) to be multiplied by 1, match 1 by 0.8, 100 by 1.2
        '''
        match_percent      = 1.0 / self.total_matches #this provides the gap, 1.0/5 = .20
        match_range        = opts.match / 2 #provides range
        match_number       = int(match[1])
        field_weight_score = self.field_weight(match_range, match_number, opts)
        weighting_percent  = field_weight_score * match_percent
        if opts.visual == True:
            print 'weight ', field_weight_score, 'number ', match_number
        return round(weighting_percent * int(match[field]), 2)

    def field_weight(self, match_range, match_number, opts):
        if (0 < match_number < match_range):
            match = match_number
            percent_increase = opts.weight - ((opts.weight * match_number) / match_range)
            return 1.0 - percent_increase
        elif match_number == match_range:
            return 1.0
        elif (match_range < match_number < ((2 * match_range) + 1)): #this works
            match = match_number - match_range
            percent_increase = (opts.weight * match) / match_range
            return 1.0 + percent_increase

class DataScoring:

    def __init__(self):
        self.sub_auto    = 1

        self.sub_agility = 2
        self.sub_speed   = 3
        self.sub_bump    = 4
        self.sub_bridge  = 6

        self.sub_dunk    = 7
        self.sub_assist  = 8
        self.sub_acquire = 9
        self.sub_strat   = 10

        self.sub_balance = 5

    def summation(self, team_scores, opts):
        for team in team_scores:
            maneuver_score    = self.maneuverability(team)
            defense_score     = self.defensive(team, maneuver_score)
            offense_score     = self.offensive(team, maneuver_score)
            collaborate_score = self.collaboration(team)
            final_score       = self.final_scoring(team, defense_score, offense_score, collaborate_score, opts)
            team.append(maneuver_score)
            team.append(defense_score)
            team.append(offense_score)
            team.append(collaborate_score)
            team.append(final_score)

        return team_scores

    def maneuverability(self, team_score):
        agility         = team_score[self.sub_agility] * 0.4
        speed           = team_score[self.sub_speed] * 0.4
        bump            = team_score[self.sub_bump] * 0.1
        bridge          = team_score[self.sub_bridge] * 0.1
        maneuver_score  = sum([agility, speed, bump, bridge]) 
        return maneuver_score

    def defensive(self, team_score, maneuver_score):
        strategy      = team_score[self.sub_strat] * 0.5
        man           = maneuver_score * 0.5
        defense_score = sum([strategy, man])
        return defense_score

    def offensive(self, team_score, maneuver_score):
        dunk          = team_score[self.sub_dunk] * 0.2
        assist        = team_score[self.sub_assist] * 0.1
        acquisition   = team_score[self.sub_acquire] * 0.1
        strategy      = team_score[self.sub_strat] * 0.3
        maneuver      = maneuver_score * 0.3
        offense_score = sum([dunk, assist, acquisition, strategy, maneuver])
        return offense_score

    def collaboration(self, team_score):
        bridge            = team_score[self.sub_bridge] * 0.3
        balance           = team_score[self.sub_balance] * 0.7
        collaborate_score = sum([bridge, balance])
        return collaborate_score

    def final_scoring(self, team_score, defense_score, offense_score, collaborate_score, opts):
        defense     = defense_score * opts.defense
        offense     = offense_score * opts.offense
        collaborate = collaborate_score * opts.collaborate
        auto        = team_score[self.sub_auto] * opts.auto
        final_score = sum([defense, offense, collaborate, auto])
        return round(final_score,3)





class DataFormat:

    def __init__(self, opts):
        self.number      = '''The number of the team in question.\\\ '''
        self.auto        = '''The team's Autonomous score. This score is calculated based on how many points they score, how consistent the robot is, and how effective their autonomous mode is. Since the maximum amount of points that can be scored during autonomous is 12 points, scoring a 12 is equivalent to a 10. No robot movement is worth a 1, and then scores are assigned based off these two extremes.\\\ '''
        self.agility     = '''How agile the robot is, how fast is it at turning, how easy is it to travel across the field? A 1 would be a robot that barely moves, or it doesn't. A robot with a 10 would be nimble and travel across the field very easily. \\\ '''
        self.speed       = '''How fast is the robot compared to the others? A 1 would be a robot that doesn't move at all. A 10 would be a robot that is the fastest robot at the competition. One that is much faster than anything else on the field. \\\ '''
        self.bump        = '''Can the robot cross the bump? If so, how fast and how effective is the robot at crossing? A 1 would be a robot that can not cross the bump, while a 10 would be a robot that can cross the bump at the same speed that it normally travels. \\\ '''
        self.balance     = '''Over all the matches, on average, how effective is the robot at balancing? A 1 would be a robot that is completely unable to balance, it falls off the bridge, or slides, or just is too imprecise to ever balance. A 10 would be a robot that can just slide to the exact spot where it needs to be without any additional correction. \\\ '''
        self.bridge      = '''Over all the matches, on average, how effective is the robot at crossing the bridge? This category includes lowering the bridge, as well as the actual transportation over it. A 1 would be a robot that can not lower the bridge on its own, and then is unable to climb up it. A 10 would be a robot that can quickly lower the bridge and then cross over it quickly and effectively. \\\ '''
        self.dunk        = '''Over all the matches, on average, how effective is the robot's scoring method? A 1 would be a robot that is completely unable to score at all. A 10 would be a robot that can score from any spot on the field, and make 100\\% of the shots in the top basket. \\\ '''
        self.assist      = '''How effective is the robot at assisting other robots in scoring? A 1 would be a robot that can not assist its team mates in scoring (maybe its range is very limited). A 10 would be one in which it can effectively place a ball into its team mates acquisition system from any spot on the field. \\\ '''
        self.acquisition = '''Over all the matches, on average, how effective is the robot's acquisition system? A 1 would be a robot that either doesn't possess an acquisition system, or maybe it's broken. A 10 would be a robot that can pick up only 3 balls quickly and be able to automatically prevent any fouling. \\\ '''
        self.strategy    = '''Over all the matches, on average, how effective is the overall team strategy? A 1 would be a robot that either just sat there, rammed itself into the wall, or fouled hundreds of points in a single round. A 10 would be a robot that always is in the right place, either scoring or assisting, or balancing. \\\ '''
        self.win         = '''Win to Loss ratio. This number is in percent. \\\ '''
        self.maneuver    = '''This score is comprised of four scores, the agility score is 40\\%, the bridge score is 10\\%, the bump score is 10\\%, and the speed score is 40\\%.\\\ '''
        self.offense     = '''This score is comprised of five scores, the acquisition score is 10\\%, the assist score is 10\\%, the strategy is 30\\%, the dunk score is 20\\%, and the maneuverability score is 30\\%.\\\ '''
        self.defense     = '''This score is comprised of two scores, the strategy and maneuverability score, both of which make up 50\\%.\\\ '''
        self.final_score = '''Over all the matches, on average, how good is the robot? This number is determined through a scoring algorithm that takes each score into account. This score is comprised of the four section scores, weighting is: defense = %f, offense = %f, collaboration = %f, and autonomous = %f. \\\ ''' % (opts.defense, opts.offense, opts.collaborate, opts.auto) 

        self.team_number        = [0, 'By Team']
        self.win_number         = [11, 'By Win Ratio']
        self.maneuver_number    = [12, 'By Maneuverability Score']
        self.defense_number     = [13, 'By Defensive Score']
        self.offense_number     = [14, 'By Offensive Score']
        self.collaborate_number = [15, 'By Collaboration Score']
        self.final_score_number = [16, 'By Final Score']
        self.print_list         = [self.team_number, self.win_number, self.maneuver_number, self.defense_number, self.offense_number ,self.collaborate_number, self.final_score_number]

    def latex_writer(self, mean_scores, opts):

        out_file = open('out_file.tex', 'w')

        out_file.write('\\documentclass[landscape, 10pt]{report} \n \n')
        out_file.write('\\usepackage{fullpage} \n')
        out_file.write('\\usepackage[top=0.75in, bottom=0.75in, left=0.25in, right=0.25in]{geometry} \n')
        out_file.write('\\usepackage{times} \n \n')
        out_file.write('\\usepackage{pdfpages} \n \n')
        out_file.write('\\usepackage{longtable} \n \n')
        out_file.write('\\usepackage{endnotes} \n \n')
        out_file.write('\\usepackage{xcolor,colortbl} \n \n')
        out_file.write('\\begin{document} \n')

        out_file.write("\\title{Scoring Results\\endnote{\\large{If you reference this report, please note that the scouting system is inherently subjective. Therefore any results are prone to error and opinion. Any team that uses Team 2945's report to make decisions realizes that Team 2945 is not liable for any mistakes made in choosing alliance members.}}} \n")
        out_file.write('\\author{Team 2945} \n')
        out_file.write('\\maketitle \n \n')

        out_file.write('\\begin{abstract} \n')
        out_file.write('\\large This program was created in order to accurately measure FIRST robotics teams effectiveness, not game scoring capabilities, as an aid to choose alliance members. This is measured through subjective scoring by individuals on ten categories entered into an excel spreadsheet exported to a .csv file. Once exported, the program is run to create a scoring analysis report. Inherent subjectivity is mitigated through documented scoring criteria and a large data pool to work with for each team.\\\ \n \\large The first step is data organization and cleansing to reduce error and format the data. Each match is weighted based on the chronological order of the match to account for teams improving as time goes on, and then the initial ten scores reported by the scouting team are used to generate four main scores, in offensive, defensive, collaborative, and autonomous capabilities. These are then run through another weighted averaging process to create a final score for each team. Once this is complete, the scoring report is written in Latex, and then compiled to PDF. \n')
        out_file.write('\\end{abstract} \n')

        out_file.write('\\begin{center} \n')
        out_file.write('Final Score weighting is: defense = %2.0f\\%% , offense = %2.0f\\%%, collaboration = %2.0f\\%%, and autonomous = %2.0f\\%%. \\\ \n' % (opts.defense * 100, opts.offense * 100, opts.collaborate * 100, opts.auto * 100))
        out_file.write('Alternate weighting upon request. \n ')
        out_file.write('\\end{center} \n \n')

        out_file.write("\\section*{Scores} \n")

        self.write_field(out_file, mean_scores, opts)

        out_file.write('\\pagebreak \n \n \\section*{Score Information} \n')

        out_file.write('\\large \n \n')

        out_file.write('\\textbf{Number: }'      + self.number      + '\n')
        out_file.write('\\textbf{Auto: }'        + self.auto        + '\n')
        out_file.write('\\textbf{Agility: }'     + self.agility     + '\n')
        out_file.write('\\textbf{Speed: }'       + self.speed       + '\n')
        out_file.write('\\textbf{Bump: }'        + self.bump        + '\n')
        out_file.write('\\textbf{Balance: }'     + self.balance     + '\n')
        out_file.write('\\textbf{Bridge: }'      + self.bridge      + '\n')
        out_file.write('\\textbf{Dunk: }'        + self.dunk        + '\n')
        out_file.write('\\textbf{Assist: }'      + self.assist      + '\n')
        out_file.write('\\textbf{Acquire: }'     + self.acquisition + '\n')
        out_file.write('\\textbf{Strategy: }'    + self.strategy    + '\n')
        out_file.write('\\textbf{Win: }'         + self.win         + '\n')
        out_file.write('\\textbf{Maneuver: }'    + self.maneuver    + '\n')
        out_file.write('\\textbf{Offense: }'     + self.offense     + '\n')
        out_file.write('\\textbf{Defense: }'     + self.defense     + '\n')
        out_file.write('\\textbf{Final Score: }' + self.final_score + '\n')

        out_file.write('\\includepdf[pages={1}]{scoring_system.pdf} \n')
        out_file.write('\\theendnotes \n')

        out_file.write('\\end{document}')
        out_file.close()


    def write_field(self, out_file, mean_scores, opts):
        if opts.report == 'all':
            for field in self.print_list:
                sorted_scores = sorted(mean_scores, key=lambda score : float(score[field[0]]))
                sorted_scores.reverse()
                out_file.write('\\subsection*{' + str(field[1]) + '} \n')

                out_file.write('\n\\begin{longtable}{l || l || l | l | l | l | l | l | l | l | l | l | l || l | l | l | l | l} \n')
                out_file.write('\\# & Team & Auto & Agility & Speed & Bump & Balance & Bridge & Dunk & Assist & Acquire & Strategy & Win (\\%) & Maneuver & Defense & Offense & Collaborate & Final Score \\\ \\hline \\endhead \n')

                row_count = 2
                number    = 1
                for row in sorted_scores:
                    self.row_writer(row, out_file, row_count, number)
                    row_count += 1
                    number += 1

                out_file.write('\end{longtable} \n \n')
                out_file.write('\\pagebreak')
        elif opts.report == 'final':
            sorted_scores = sorted(mean_scores, key=lambda score : float(score[self.print_list[6][0]]))
            sorted_scores.reverse()
            out_file.write('\\subsection*{' + str(self.print_list[6][1]) + '} \n')

            out_file.write('\n\\begin{longtable}{l || l || l | l | l | l | l | l | l | l | l | l | l || l | l | l | l | l} \n')
            out_file.write('\\# & Team & Auto & Agility & Speed & Bump & Balance & Bridge & Dunk & Assist & Acquire & Strategy & Win (\\%) & Maneuver & Defense & Offense & Collaborate & Final Score \\\ \\hline \\endhead \n')

            row_count = 2
            number    = 1
            for row in sorted_scores:
                self.row_writer(row, out_file, row_count, number)
                row_count += 1
                number += 1

            out_file.write('\end{longtable} \n \n')
            out_file.write('\\pagebreak')
            
        

    def row_writer(self, row, out_file, row_count, number):
        item_count = 1
        if (row_count % 2) == 0:
            out_file.write('\\rowcolor{lightgray}')
        out_file.write(str(number) + ' & ')
        for item in row:
            out_file.write(str(item))
            if item_count != 17:
                out_file.write(' & ')
            item_count += 1
        out_file.write('\\\ \n')


class Log_File_Generation:

    def __init__(self):
        self.logfile = open('logfile.txt', mode='a')

    def log_clean(self):
        clean = open('logfile.txt', mode='w')
        clean.close()

def get_opts():
    global opts
    global args
    parser = optparse.OptionParser(usage = 'Usage = %prog <options>', version = 'Version 1.0')
    parser.add_option('-d', '--defense', 
                       action='store',
                       type='float',
                       default=0.3,
                       help='Weighting for defensive score')
    parser.add_option('-o', '--offense', 
                       action='store',
                       type='float',
                       default=0.3,
                       help='Weighting for defensive score')
    parser.add_option('-c', '--collaborate', 
                       action='store',
                       type='float',
                       default=0.2,
                       help='Weighting for defensive score')
    parser.add_option('-a', '--auto', 
                       action='store',
                       type='float',
                       default=0.2,
                       help='Weighting for defensive score')
    parser.add_option('-m', '--match', 
                       action='store',
                       type='int',
                       default=100,
                       help='How many matches were played total')
    parser.add_option('-w', '--weight', 
                       action='store',
                       type='float',
                       default=0.2,
                       help='The degree of match weighting')
    parser.add_option('-v', '--visual', 
                       action='store',
                       type='int',
                       default=0,
                       help='Debug mode, visual commands')
    parser.add_option('-r', '--report', 
                       action='store',
                       type='string',
                       default='all',
                       help='Type of report')
    opts, args = parser.parse_args()


    if (sum([opts.defense, opts.offense, opts.collaborate, opts.auto])) != 1:
        print "ERROR 5: Options must add up to 1"
        print opts.defense, opts.offense, opts.collaborate, opts.auto
        sys.exit(0)
    if (0 > opts.weight > 1):
        print "ERROR 6: Weight argument must be between 0 and 1"
        print opts.weight
        sys.exit(0)
    if opts.visual not in [True, False]:
        print "ERROR 7: Visual must be 0 or 1"
        print opts.visual
        sys.exit(0)
    if opts.visual == 0:
        opts.visual = False
    elif opts.visual == 1:
        opts.visual = True
    type_list = ['all', 'final']
    if opts.report not in type_list:
        print 'ERROR 9: Report must be in ', type_list
        print opts.report
        sys.exit(0)

    return opts


if __name__ == "__main__":
    sys.exit(main())
