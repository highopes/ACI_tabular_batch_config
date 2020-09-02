# ACI Batch Configuration Using CSV/XLS Format Files

## Description

The GUI-style networking configuration has a smoother learning curve for beginners, but is cumbersome for engineers who have to do a lot of day-to-day operations, especially Cisco ACI. This tool provides batch configuration input via CSV/XLS based tabulated files, which is very useful for engineers with relatively fixed configuration mode who only need to complete repetitive daily deployment in large quantities.

This tool has basic format checking capabilities for tabulated files, provides template downloads, and the ability to determine the validity of values in a table, as well as the ability to perform result reporting and rollback (in the future).

## Installation

The tool dosen't need to install. It's a python script directly running in your python environment.

## Environment

Required <br>
* Python 3+ <br>
* ACI and compatible ACI Cobra SDK (e.g. support microsegmentation feature of ACI) <br>


Currently this tool is used only for demo purpose. For productive usage, please contact the author at: weihang_hank@gmail.com