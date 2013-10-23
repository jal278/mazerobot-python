//---------------------------------------------------------------------------
//
// Name:        mazeApp.h
// Author:      Administrator
// Created:     2/5/2008 9:20:51 PM
// Description: 
//
//---------------------------------------------------------------------------

#ifndef __MAZEDLGApp_h__
#define __MAZEDLGApp_h__

#ifdef __BORLANDC__
	#pragma hdrstop
#endif

#ifndef WX_PRECOMP
	#include <wx/wx.h>
#else
	#include <wx/wxprec.h>
#endif
#include <wx/cmdline.h>
class mazeDlgApp : public wxApp
{
	public:
    wxArrayString files;
		bool OnInit();
		int OnExit();
    virtual void OnInitCmdLine(wxCmdLineParser& parser);
    virtual bool OnCmdLineParsed(wxCmdLineParser& parser);
};

static const wxCmdLineEntryDesc g_cmdLineDesc [] =
{
     { wxCMD_LINE_PARAM, NULL, NULL, wxT("disables the GUI"),wxCMD_LINE_VAL_STRING, wxCMD_LINE_PARAM_MULTIPLE },
 
     { wxCMD_LINE_NONE }
};
DECLARE_APP(mazeDlgApp)
#endif
