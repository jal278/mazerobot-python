//---------------------------------------------------------------------------
//
// Name:        mazeApp.cpp
// Author:      Administrator
// Created:     2/5/2008 9:20:51 PM
// Description: 
//
//---------------------------------------------------------------------------

#include "mazeApp.h"
#include "mazeDlg.h"
#include "population.h"
#include <stdio.h>

IMPLEMENT_APP(mazeDlgApp)
bool mazeDlgApp::OnInit()
{
if (!wxApp::OnInit())
        return false;
cout << "INIT" << endl;
	mazeDlg* dialog = new mazeDlg(NULL,files[0],files[1],files[2]);
	SetTopWindow(dialog);
	dialog->Show(true);		
return true;
}
 
int mazeDlgApp::OnExit()
{
	return 0;
}

void mazeDlgApp::OnInitCmdLine(wxCmdLineParser& parser)
{
    parser.SetDesc (g_cmdLineDesc);
    // must refuse '/' as parameter starter or cannot use "/path" style paths
    parser.SetSwitchChars (wxT("-"));
}
 
bool mazeDlgApp::OnCmdLineParsed(wxCmdLineParser& parser)
{
    if(parser.GetParamCount()<2) {
     cout << "Call Format: ./maze <maze file> <brain file>" << endl;
     exit(0);
    }

    // to get at your unnamed parameters use
    for (int i = 0; i < parser.GetParamCount(); i++)
    {
            files.Add(parser.GetParam(i));
	    cout << files[i].mb_str() << endl;
    }
 
    // and other command line parameters
 
    // then do what you need with them.
 
    return true;
}
