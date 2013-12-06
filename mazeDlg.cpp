//---------------------------------------------------------------------------
//
// Name:        mazeDlg.cpp
// Author:      Administrator
// Created:     2/5/2008 9:20:51 PM
// Description: mazeDlg class implementation
//
//---------------------------------------------------------------------------

#include "mazeDlg.h"
#include "population.h"
#include "experiments.h"
#include <math.h>
#include <iostream>
#include <fstream>
#include <stdio.h>
using namespace std;
//Do not add custom headers
//wxDev-C++ designer will remove them
////Header Include Start
////Header Include End

//----------------------------------------------------------------------------
// mazeDlg
//----------------------------------------------------------------------------
//Add Custom Events only in the appropriate block.
//Code added in other places will be removed by wxDev-C++
////Event Table Start
BEGIN_EVENT_TABLE(mazeDlg,wxDialog)
	////Manual Code Start
	EVT_TIMER(1,mazeDlg::OnTimer)
	////Manual Code End
	
	EVT_CLOSE(mazeDlg::OnClose)
	EVT_KEY_DOWN(mazeDlg::OnKeyDown)
	EVT_PAINT(mazeDlg::OnPaint)
	EVT_LEFT_DOWN(mazeDlg::OnLeftDown)
	EVT_RIGHT_DOWN(mazeDlg::OnRightDown)
	EVT_MOUSEWHEEL(mazeDlg::OnMouseWheel)

	
END_EVENT_TABLE()
////Event Table End

mazeDlg::mazeDlg(wxWindow *parent, const wxString &mazefile, const wxString &brainfile, const wxString &seedString,wxWindowID id, const wxString &title, const wxPoint &position, const wxSize& size, long style)
: wxDialog(parent, id, title, position, size, style)
{
        int seed = atoi(seedString.mb_str());
        if (seed==-1) {
	srand(time(NULL));
        }
	else {
	cout <<"SEED" << seed << endl;
	srand(seed);
	}
	envCounter=0;
	CreateGUIControls();
	fitness=0.0;
	timestep=0;
        newpop=NULL;
        brainstring=brainfile;


        newpop=new NEAT::Population(brainstring.mb_str());
        net=(newpop->organisms[0]->net);
	//newpop=new NEAT::Population(brainfile.mb_str());
	//net=(newpop->organisms[0]->net);
	//net->print_links_tofile("links.out");

        read_in_environments(mazefile.mb_str(), envList);

        load_next_environment();
	//Environment *env1=new Environment(mazefile.mb_str());
	//env1->goalattract=false;
        //env=mazesimIni(env1,net,dc);

	timer = new wxTimer(this, 1);
	timer->Start(10); //was 50
	humancontrol=false;
}

void mazeDlg::load_next_environment() {

 net->flush();
 if(envCounter==0) { 
    envList[0]->communication_input=0.0;
 }
 else {
  envList[envCounter]->communication_input = env->communication_output;
  cout << "sx " << env->hero.start.x << " " << env->hero.start.y << endl;
  cout << "ci " << env->communication_input << " co: "<< env->communication_output << endl;
 }

 envList[envCounter]->goalattract=true;
 env=mazesimIni(envList[envCounter],net,dc);
}

mazeDlg::~mazeDlg()
{
  ofstream out("route.txt");
  for(int x=0;x<xc.size();x++)
	out << xc[x] << " " << yc[x] << endl;
  out.close();
    delete env;
   delete newpop;
} 

void mazeDlg::CreateGUIControls()
{
	//Do not add custom code between
	//GUI Items Creation Start and GUI Items Creation End.
	//wxDev-C++ designer will remove them.
	//Add the custom code before or after the blocks
	////GUI Items Creation Start

	SetTitle(wxT("maze"));
	SetIcon(wxNullIcon);
	SetSize(8,8,900,700);
	Center();
	
	////GUI Items Creation End
}
void mazeDlg::OnTimer(wxTimerEvent& event)
{
   
    for(int i=0;i<1;i++)
	{	
	xc.push_back(env->hero.location.x);
	yc.push_back(env->hero.location.y);
	double fit=0.0;
	if(!humancontrol) {
		fit=mazesimStep(env,net,dc);
        }
	else
		env->Update();
	//env->hero.collide=false;
	
        //cout << env->hero.collisions << endl;
	if(timestep<(env->steps-1)) {
         fitness+=fit;	
	 timestep++;
	}

        else {
	 //if(envCounter<(envList.size()-1)) {
		timestep=0;
		envCounter++;
		envCounter=envCounter%(envList.size());
		load_next_environment();
         // }
	}
   }
    Refresh();
}
void mazeDlg::OnPaint(wxPaintEvent& event)
{
  float scale=1.0;
  wxPaintDC dc(this);
  float rad = env->hero.heading/180.0*3.1415926;
  dc.SetPen(*wxBLACK_PEN);
  
  wxPen newpen(*wxGREEN_PEN);
  newpen.SetWidth(5);
  wxPen heropen(*wxRED_PEN);
  heropen.SetWidth(3);
  
  //draw inputs
 //double inputs[30];
 //env->generate_neural_inputs(inputs); 
if(true)
 for(int i=0;i<net->inputs.size();i++)
  {
   dc.SetBrush(*wxBLACK_BRUSH);
   double input = net->inputs[i]->activation;
   dc.DrawCircle(i*30+20,500,(int)(10.0));

   if(input>0.5)
   dc.SetBrush(*wxGREEN_BRUSH);
   else
   dc.SetBrush(*wxBLUE_BRUSH);
   dc.DrawCircle(i*30+20,500,(int)(input*10.0));
  }

 
 for(int i=0;i<2;i++)
  {
   dc.SetBrush(*wxBLACK_BRUSH);
   dc.DrawCircle(i*30+20,550,10);
   double val=net->outputs[i]->activation;
   if(val>0.5)
   dc.SetBrush(*wxGREEN_BRUSH);
   else
   dc.SetBrush(*wxBLUE_BRUSH);
   dc.DrawCircle(i*30+20,550,(int)(val*10.0));
  }
 
 //draw walls
  for(int i=0;i<env->lines.size();i++)
  {
  wxCoord x1 = scale*env->lines[i]->a.x, y1=scale*env->lines[i]->a.y;
  wxCoord x2 = scale*env->lines[i]->b.x, y2=scale*env->lines[i]->b.y;
  dc.DrawLine(x1, y1, x2, y2);
  }
  
  //draw target
  dc.SetBrush(*wxGREEN_BRUSH);
  wxCoord ex = scale*env->end.x;
  wxCoord ey = scale*env->end.y;
  if(!env->reachgoal)
  dc.DrawCircle(ex,ey,10);

  dc.SetBrush(*wxBLUE_BRUSH);
  wxCoord poix = scale*env->poi.x;
  wxCoord poiy = scale*env->poi.y;
  if(!env->reachpoi)
  dc.DrawCircle(poix,poiy,10);
 
 //draw hero 
  wxCoord x = scale*env->hero.location.x;
  wxCoord y = scale*env->hero.location.y;
  dc.SetBrush(*wxWHITE_BRUSH);
  dc.DrawCircle(x,y,env->hero.radius*scale);

  //draw radar
  bool onflag=false;


 for(int i=0;i<env->hero.radar.size();i++)
 {
        if(env->hero.poi_radar[i]>0.0)
        {
            onflag=true;
            
            dc.SetPen(newpen);
        }
        else
        {
            dc.SetPen(*wxBLACK_PEN);
            
        }
            float ang1=env->hero.heading+env->hero.radarAngles1[i];
            if(ang1>360) ang1-=360;
            float ang2=env->hero.heading+env->hero.radarAngles2[i];
            if(ang2>360) ang2-=360;
            
            wxCoord x1 = x+cos((ang1)/180.0*3.1415)*env->hero.radius*scale;
            wxCoord y1 = y+sin((ang1)/180.0*3.1415)*env->hero.radius*scale;
            dc.DrawLine(x,y,x1,y1);
            x1 = x+cos((ang2)/180.0*3.1415)*env->hero.radius*scale;
            y1 = y+sin((ang2)/180.0*3.1415)*env->hero.radius*scale;
            dc.DrawLine(x,y,x1,y1);
            
  }

 
  
  dc.SetPen(*wxBLACK_DASHED_PEN);
  //draw rangefinders
  if(true)
  for(int i=0;i<env->hero.rangeFinders.size();i++)
  {
        Point p1=env->hero.location;
        Point p2(p1);
        p2.x+=cos(rad)*env->hero.rangeFinders[i];
        p2.y+=sin(rad)*env->hero.rangeFinders[i];
        p2.rotate(env->hero.rangeFinderAngles[i],p1);
        dc.DrawLine(p1.x*scale,p1.y*scale,p2.x*scale,p2.y*scale);
  }
  
  //show orientation
  dc.SetPen(heropen);
  
  float nx=env->hero.location.x+cos(rad)*env->hero.radius;
  float ny=env->hero.location.y+sin(rad)*env->hero.radius;
  wxCoord x1=scale*nx;
  wxCoord y1=scale*ny;
  dc.DrawLine(x,y,x1,y1);

 //draw Fitness
 wxString outstring;
 
if(true)
 outstring.Printf(_T("Timestep: %d, Fitness: %f"), timestep, fitness);
 dc.DrawText(outstring,50,600);
 

  
}

void mazeDlg::OnClose(wxCloseEvent& /*event*/)
{
	Destroy();
}

/*
 * mazeDlgKeyDown
 */
void mazeDlg::OnLeftDown(wxMouseEvent& event)
{
	env->hero.ang_vel-=1;
	if(humancontrol==false)
	{
		env->hero.ang_vel=0.0;
		env->hero.speed=0.0;
	}
	humancontrol=true;
	
	//  wxMessageBox(_T("Click1"), _T("Click"),
   //wxOK | wxICON_INFORMATION, this);
	event.Skip();
}
void mazeDlg::OnRightDown(wxMouseEvent& event)
{
	env->hero.ang_vel+=1;
//	  wxMessageBox(_T("Click1"), _T("Click"),
 //  wxOK | wxICON_INFORMATION, this);
	event.Skip();
}
void mazeDlg::OnMouseWheel(wxMouseEvent& event)
{
	//  wxMessageBox(_T("Click1"), _T("Click"),
   //wxOK | wxICON_INFORMATION, this);
 //	event.Skip();
	env->hero.speed+=event.GetWheelRotation()/event.GetWheelDelta();
}
void mazeDlg::OnKeyDown(wxKeyEvent& event)
{
    #define ASCII_LEFT 97
    #define ASCII_RIGHT 100
    #define ASCII_UP 119
    #define ASCII_DOWN 115
	// insert your code here
	int code = event.GetKeyCode();
	
	//ofstream out("out.txt");
	//out << code << endl;
	//out.close();
        
	if(code=='A') env->hero.ang_vel-=1; //env->hero.heading-=15.0;
	if(code=='D') env->hero.ang_vel+=1; //env->hero.heading+=15.0;
	if(code=='W') env->hero.speed+=0.5;
	if(code=='S') env->hero.speed-=0.5;
	if(env->hero.heading<-360) env->hero.heading+=360;
	if(env->hero.heading>360) env->hero.heading-=360;
			  wxMessageBox(_T("Click1"), _T("Click"),
   wxOK | wxICON_INFORMATION, this);
	event.Skip();
}
