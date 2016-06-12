\version "2.18.2"
\language "english"

\markup {
  \score {
    \new StaffGroup <<
                                % remove brace for this staffgroup
      \override StaffGroup.SystemStartBracket.collapse-height = #2000.0
      
      \new StaffGroup <<
                                % remove brace for this staffgroup
        \override StaffGroup.SystemStartBracket.collapse-height = #20.0
        \new Staff {
          e f g
        }
      >>
    >>
    \layout {
      
      \context {
        \Score
                                % remove increase spaces between staff groups in a staff group
        \override StaffGrouper.staffgroup-staff-spacing = #'((basic-distance . 30) (padding . 1))
        \override BarLine.allow-span-bar = ##f % remove inter-staff barline
        \override SystemStartBar.collapse-height = #2000 % remove start bar
      }

      \context Staff = "to right" {
        
      }
    }
  }
}

\markup {
  \fill-line {
    \score {
      \new StaffGroup <<
        \override StaffGroup.SystemStartBracket.collapse-height = #20.0
        \new Staff = "to right" {
          a b c'
        }
      >>
      \layout {
        
        \context {
          \Score
                                % remove increase spaces between staff groups in a staff group
          \override StaffGrouper.staffgroup-staff-spacing = #'((basic-distance . 30) (padding . 1))
          \override BarLine.allow-span-bar = ##f % remove inter-staff barline
          \override SystemStartBar.collapse-height = #2000 % remove start bar
        }
      }
    }
  }
}