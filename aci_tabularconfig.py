#!/usr/bin/env python
###################################################################################
#                           Written by Wei, Hang                                  #
#                          weihang_hank@gmail.com                                 #
###################################################################################
"""
Batch config ACI model elements with tabular information (from excel/csv file)
"""
import tkinter as tk
from tkinter import filedialog, dialog, messagebox
import os
import csv
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.pol
import cobra.model.fv
import cobra.model.vz
import cobra.model.vmm
from credentials import *
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TKinter initialization
window = tk.Tk()
window.title('Table/CSV-based Configuration for ACI 0.1 by Wei Hang')  # Title
window.geometry('1000x500')  # Window Size

ROWS = []  # Configuration content from CSV file
CONFIG_READY = False  # Flag to show if config data is ready

# Table header and the key index. Change here and function 'push_config' if want a new template
HEADER = ['Id', 'Tenant', 'VRF', 'BD', 'App Profile', 'EPG', 'VM Domain', 'BM Domain', 'Prov Contract', 'Cons Contract',
          'Contract']
i_id = HEADER.index('Id')
i_tenant = HEADER.index('Tenant')
i_vrf = HEADER.index('VRF')
i_bd = HEADER.index('BD')
i_ap = HEADER.index('App Profile')
i_epg = HEADER.index('EPG')
i_vmm = HEADER.index('VM Domain')
i_bmm = HEADER.index('BM Domain')
i_pctr = HEADER.index('Prov Contract')
i_cctr = HEADER.index('Cons Contract')
i_ctr = HEADER.index('Contract')

# text1 is the main text widget in the main window
text1 = tk.Text(window, width=138, height=24, font=('Arial', 10))
text1.place(x=15, y=15, anchor='nw')
text1.tag_config("warning", foreground="red")
text1.tag_config("config", foreground="blue")
text1.insert('insert', "Please click button 'Open CSV File' to load a config file. \n")


def open_file():
    """
    Open CSV File
    """
    global ROWS, CONFIG_READY  # keep the value when exit this function

    file_path = filedialog.askopenfilename(title=u'Open CSV File')
    text1.insert('insert', '\nNow open file at ' + file_path + '\n')
    if file_path:  # if file_path exists, then...
        try:  # open and load the config data to a list
            with open(file=file_path, mode='r', encoding='utf-8') as csvFile:
                reader = csv.reader(csvFile)
                ROWS = [row for row in reader]  # ROWS contain all the config data now and it's a list
                if ROWS[0] != HEADER:  # judge the table header
                    text1.insert('insert',
                                 "\n Sorry, it's not the CSV we can support. Please download the latest template.\n",
                                 "warning")
                    return
                text1.insert('insert', "\nNow loading following configuration ... \n", )
                for row in ROWS:
                    text1.insert('insert', row, "config")
                    text1.insert('insert', '\n')
                text1.insert('insert',
                             "\nIf you want to push above config to your ACI, please click button: Push Config\n")
                CONFIG_READY = True  # it's ready for pushing config
                bt_push["state"] = "normal"
        except:
            text1.insert('insert', "\nThere're invalid characters in the file. Try to modify and reopen it.  \n",
                         "warning")
            CONFIG_READY = False  # it's not ready to push config
            bt_push["state"] = "disabled"


def push_config():
    """
    Push Config to ACI
    """
    text1.insert('insert', "\nTaking a snapshot in case you need to restore the configuration in the future.\n")
    # Todo: Taking snapshot of ACI current config

    # push config to ACI
    try:  # login to the ACI
        text1.insert('insert', "Login to the ACI... " + URL + "\n")
        ls = cobra.mit.session.LoginSession(URL, LOGIN, PASSWORD)
        md = cobra.mit.access.MoDirectory(ls)
        md.login()
        text1.insert('insert', "Login successfully. Pushing Config ... \n")
    except:
        text1.insert('insert', "\n Login failed. Check the credentials\n", "warning")
        print("login failed")
        return

    # construct and submit the config row by row
    headerflag = True  # flag shows if current row is the header
    Success = True  # flag shows if all lines successfully complete
    for row in ROWS:
        if headerflag:
            headerflag = False
            continue  # bypass the fist row (header)
        # non-header rows processing
        try:
            polUni = cobra.model.pol.Uni('')
            if row[i_tenant]:  # Tenant
                fvTenant = cobra.model.fv.Tenant(polUni, row[i_tenant])
                if row[i_vrf]:  # VRF
                    fvCtx = cobra.model.fv.Ctx(fvTenant, name=row[i_vrf])
                if row[i_bd]:  # BD
                    fvBD = cobra.model.fv.BD(fvTenant, name=row[i_bd])
                    if row[i_vrf]:  # Associate BD to VRF
                        fvRsCtx = cobra.model.fv.RsCtx(fvBD, tnFvCtxName=row[i_vrf])
                if row[i_ctr]:  # contract
                    vzBrCP = cobra.model.vz.BrCP(fvTenant, name=row[i_ctr])
                    vzSubj = cobra.model.vz.Subj(vzBrCP, name='Subject', revFltPorts='yes')
                    vzRsSubjFiltAtt = cobra.model.vz.RsSubjFiltAtt(vzSubj, action='permit',
                                                                   priorityOverride='default',
                                                                   tnVzFilterName='default')
                if row[i_ap]:  # AP
                    fvAp = cobra.model.fv.Ap(fvTenant, name=row[i_ap])
                    if row[i_epg]:  # EPG
                        fvAEPg = cobra.model.fv.AEPg(fvAp, name=row[i_epg])
                        if row[i_bd]:  # Associate EPG to BD
                            fvRsBd = cobra.model.fv.RsBd(fvAEPg, tnFvBDName=row[i_bd])
                        if row[i_vmm]:  # Associate EPG to VMM Domain
                            fvRsDomAtt = cobra.model.fv.RsDomAtt(fvAEPg,
                                                                 tDn='uni/vmmp-VMware/dom-' + row[i_vmm])
                        if row[i_bmm]:  # Associate EPG to BM Domain
                            # Todo:
                            pass
                        if row[i_cctr]:  # Consume a contract
                            fvRsCons = cobra.model.fv.RsCons(fvAEPg, tnVzBrCPName=row[i_cctr])
                        if row[i_pctr]:  # Provide a contract
                            fvRsProv = cobra.model.fv.RsProv(fvAEPg, tnVzBrCPName=row[i_pctr])

                # submit the config request for this row
                c = cobra.mit.request.ConfigRequest()
                c.addMo(fvTenant)
                md.commit(c)
                text1.insert('insert', "Successful for Line " + row[i_id] + "\n", "config")
        except:
            Success = False
            text1.insert('insert',
                         "Line: '" + row[i_id] + "' has error. This line may not fully implement. \n", "warning")

    if Success:
        text1.insert('insert', "\nSuccessful for all lines! \n", "config")
    else:
        text1.insert('insert', "\nNot all lines were successful, see details above \n", "warning")


def save_file():
    """
    Download template
    """
    file_path = filedialog.asksaveasfilename(title=u'Save Template as...')
    if file_path:
        text1.insert('insert', 'Downloading Template ...\n')
        with open(file=file_path, mode='w', encoding='utf-8', newline='') as csvFile:
            writer = csv.writer(csvFile, dialect='excel')
            # write the table header
            writer.writerow(HEADER)
            text1.insert('insert', 'Template Downloaded\n')


def do_exit():
    """
    doing exit
    """
    exit(0)


bt_download = tk.Button(window, text='Download Template', width=15, height=2, font=("Arial", 10), command=save_file)
bt_download.place(x=55, y=430, anchor='nw')

bt_open = tk.Button(window, text='Open CSV File', width=15, height=2, font=("Arial", 10), command=open_file)
bt_open.place(x=310, y=430, anchor='nw')

bt_push = tk.Button(window, text='Push Config', width=15, height=2, font=("Arial", 10), command=push_config)
bt_push.place(x=565, y=430, anchor='nw')

# set the default status of PUSH button
if not CONFIG_READY:
    bt_push["state"] = "disabled"

bt_exit = tk.Button(window, text='Exit', width=15, height=2, font=("Arial", 10), command=do_exit)
bt_exit.place(x=810, y=430, anchor='nw')

window.mainloop()  # loop
