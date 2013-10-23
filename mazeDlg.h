//---------------------------------------------------------------------------
//
// Name:        mazeDlg.h
// Author:      Administrator
// Created:     2/5/2008 9:20:51 PM
// Description: mazeDlg class declaration
//
//---------------------------------------------------------------------------

#ifndef __MAZEDLG_h__
#define __MAZEDLG_h__

#ifdef __BORLANDC__
	#pragma hdrstop
#endif

#ifndef WX_PRECOMP
	#include <wx/wx.h>
	#include <wx/dialog.h>
#else
	#include <wx/wxprec.h>
#endif

#include "maze.h"
#include "network.h"
#include "population.h"
#include <vector>
using namespace std;
//Do not add custom headers between 
//Header Include Start and Header Include End.
//wxDev-C++ designer will remove them. Add custom headers after the block.
////Header Include Start
////Header Include End

////Dialog Style Start
#undef mazeDlg_STYLE
#define mazeDlg_STYLE wxCAPTION | wxSYSTEM_MENU | wxDIALOG_NO_PARENT | wxMINIMIZE_BOX | wxCLOSE_BOX
////Dialog Style End

class mazeDlg : public wxDialog
{
	private:
		DECLARE_EVENT_TABLE();
		
	public:
	vector< vector< float> > dc;
	vector<float> xc;
	vector<float> yc;
	NEAT::Network* net;
	double fitness;
	int timestep;
	bool humancontrol;
	NEAT::Population* newpop;
        wxTimer *timer;
		mazeDlg(wxWindow *parent, const wxString &mazefile=wxT("maze.txt"), const wxString &brainfile=wxT("mazebrain.dat"),wxWindowID id = 1, const wxString &title = wxT("maze"), const wxPoint& pos = wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = mazeDlg_STYLE);
		virtual ~mazeDlg();
		Environment *env;
	
	
	private:
		//Do not add custom control declarations between 
		//GUI Control Declaration Start and GUI Control Declaration End.
		//wxDev-C++ will remove them. Add custom code after the block.
		////GUI Control Declaration Start
		////GUI Control Declaration End
		
	private:
		//Note: if you receive any error with these enum IDs, then you need to
		//change your old form code that are based on the #define control IDs.
		//#defines may replace a numeric value for the enum names.
		//Try copy and pasting the below block in your old form header files.
		enum
		{
			////GUI Enum Control ID Start
			////GUI Enum Control ID End
			ID_DUMMY_VALUE_ //don't remove this value unless you have other enum values
		};
	
	private:
		void OnClose(wxCloseEvent& event);
		void OnPaint(wxPaintEvent& event);
		void OnTimer(wxTimerEvent& event);
		void OnKeyDown(wxKeyEvent& event);
		void OnLeftDown(wxMouseEvent& event);
		void OnRightDown(wxMouseEvent& event);
		void OnMouseWheel(wxMouseEvent& event);
		void CreateGUIControls();
};

#endif
