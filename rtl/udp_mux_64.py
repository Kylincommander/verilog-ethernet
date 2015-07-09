#!/usr/bin/env python
"""udp_mux_64

Generates an UDP mux with the specified number of ports

Usage: udp_mux_64 [OPTION]...
  -?, --help     display this help and exit
  -p, --ports    specify number of ports
  -n, --name     specify module name
  -o, --output   specify output file name
"""

import io
import sys
import getopt
import math
from jinja2 import Template

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "?n:p:o:", ["help", "name=", "ports=", "output="])
        except getopt.error as msg:
             raise Usage(msg)
        # more code, unchanged  
    except Usage as err:
        print(err.msg, file=sys.stderr)
        print("for help use --help", file=sys.stderr)
        return 2

    ports = 4
    name = None
    out_name = None

    # process options
    for o, a in opts:
        if o in ('-?', '--help'):
            print(__doc__)
            sys.exit(0)
        if o in ('-p', '--ports'):
            ports = int(a)
        if o in ('-n', '--name'):
            name = a
        if o in ('-o', '--output'):
            out_name = a

    if name is None:
        name = "udp_mux_64_{0}".format(ports)

    if out_name is None:
        out_name = name + ".v"

    print("Opening file '%s'..." % out_name)

    try:
        out_file = open(out_name, 'w')
    except Exception as ex:
        print("Error opening \"%s\": %s" %(out_name, ex.strerror), file=sys.stderr)
        exit(1)

    print("Generating {0} port UDP mux {1}...".format(ports, name))

    select_width = int(math.ceil(math.log(ports, 2)))

    t = Template(u"""/*

Copyright (c) 2014 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

*/

// Language: Verilog 2001

`timescale 1ns / 1ps

/*
 * UDP {{n}} port multiplexer (64 bit datapath)
 */
module {{name}}
(
    input  wire        clk,
    input  wire        rst,
    
    /*
     * UDP frame inputs
     */
{%- for p in ports %}
    input  wire        input_{{p}}_udp_hdr_valid,
    output wire        input_{{p}}_udp_hdr_ready,
    input  wire [47:0] input_{{p}}_eth_dest_mac,
    input  wire [47:0] input_{{p}}_eth_src_mac,
    input  wire [15:0] input_{{p}}_eth_type,
    input  wire [3:0]  input_{{p}}_ip_version,
    input  wire [3:0]  input_{{p}}_ip_ihl,
    input  wire [5:0]  input_{{p}}_ip_dscp,
    input  wire [1:0]  input_{{p}}_ip_ecn,
    input  wire [15:0] input_{{p}}_ip_length,
    input  wire [15:0] input_{{p}}_ip_identification,
    input  wire [2:0]  input_{{p}}_ip_flags,
    input  wire [12:0] input_{{p}}_ip_fragment_offset,
    input  wire [7:0]  input_{{p}}_ip_ttl,
    input  wire [7:0]  input_{{p}}_ip_protocol,
    input  wire [15:0] input_{{p}}_ip_header_checksum,
    input  wire [31:0] input_{{p}}_ip_source_ip,
    input  wire [31:0] input_{{p}}_ip_dest_ip,
    input  wire [15:0] input_{{p}}_udp_source_port,
    input  wire [15:0] input_{{p}}_udp_dest_port,
    input  wire [15:0] input_{{p}}_udp_length,
    input  wire [15:0] input_{{p}}_udp_checksum,
    input  wire [63:0] input_{{p}}_udp_payload_tdata,
    input  wire [7:0]  input_{{p}}_udp_payload_tkeep,
    input  wire        input_{{p}}_udp_payload_tvalid,
    output wire        input_{{p}}_udp_payload_tready,
    input  wire        input_{{p}}_udp_payload_tlast,
    input  wire        input_{{p}}_udp_payload_tuser,
{% endfor %}
    /*
     * UDP frame output
     */
    output wire        output_udp_hdr_valid,
    input  wire        output_udp_hdr_ready,
    output wire [47:0] output_eth_dest_mac,
    output wire [47:0] output_eth_src_mac,
    output wire [15:0] output_eth_type,
    output wire [3:0]  output_ip_version,
    output wire [3:0]  output_ip_ihl,
    output wire [5:0]  output_ip_dscp,
    output wire [1:0]  output_ip_ecn,
    output wire [15:0] output_ip_length,
    output wire [15:0] output_ip_identification,
    output wire [2:0]  output_ip_flags,
    output wire [12:0] output_ip_fragment_offset,
    output wire [7:0]  output_ip_ttl,
    output wire [7:0]  output_ip_protocol,
    output wire [15:0] output_ip_header_checksum,
    output wire [31:0] output_ip_source_ip,
    output wire [31:0] output_ip_dest_ip,
    output wire [15:0] output_udp_source_port,
    output wire [15:0] output_udp_dest_port,
    output wire [15:0] output_udp_length,
    output wire [15:0] output_udp_checksum,
    output wire [63:0] output_udp_payload_tdata,
    output wire [7:0]  output_udp_payload_tkeep,
    output wire        output_udp_payload_tvalid,
    input  wire        output_udp_payload_tready,
    output wire        output_udp_payload_tlast,
    output wire        output_udp_payload_tuser,

    /*
     * Control
     */
    input  wire        enable,
    input  wire [{{w-1}}:0]  select
);

reg [{{w-1}}:0] select_reg = 0, select_next;
reg frame_reg = 0, frame_next;
{% for p in ports %}
reg input_{{p}}_udp_hdr_ready_reg = 0, input_{{p}}_udp_hdr_ready_next;
{%- endfor %}
{% for p in ports %}
reg input_{{p}}_udp_payload_tready_reg = 0, input_{{p}}_udp_payload_tready_next;
{%- endfor %}

reg output_udp_hdr_valid_reg = 0, output_udp_hdr_valid_next;
reg [47:0] output_eth_dest_mac_reg = 0, output_eth_dest_mac_next;
reg [47:0] output_eth_src_mac_reg = 0, output_eth_src_mac_next;
reg [15:0] output_eth_type_reg = 0, output_eth_type_next;
reg [3:0]  output_ip_version_reg = 0, output_ip_version_next;
reg [3:0]  output_ip_ihl_reg = 0, output_ip_ihl_next;
reg [5:0]  output_ip_dscp_reg = 0, output_ip_dscp_next;
reg [1:0]  output_ip_ecn_reg = 0, output_ip_ecn_next;
reg [15:0] output_ip_length_reg = 0, output_ip_length_next;
reg [15:0] output_ip_identification_reg = 0, output_ip_identification_next;
reg [2:0]  output_ip_flags_reg = 0, output_ip_flags_next;
reg [12:0] output_ip_fragment_offset_reg = 0, output_ip_fragment_offset_next;
reg [7:0]  output_ip_ttl_reg = 0, output_ip_ttl_next;
reg [7:0]  output_ip_protocol_reg = 0, output_ip_protocol_next;
reg [15:0] output_ip_header_checksum_reg = 0, output_ip_header_checksum_next;
reg [31:0] output_ip_source_ip_reg = 0, output_ip_source_ip_next;
reg [31:0] output_ip_dest_ip_reg = 0, output_ip_dest_ip_next;
reg [15:0] output_udp_source_port_reg = 0, output_udp_source_port_next;
reg [15:0] output_udp_dest_port_reg = 0, output_udp_dest_port_next;
reg [15:0] output_udp_length_reg = 0, output_udp_length_next;
reg [15:0] output_udp_checksum_reg = 0, output_udp_checksum_next;

// internal datapath
reg [63:0] output_udp_payload_tdata_int;
reg [7:0]  output_udp_payload_tkeep_int;
reg        output_udp_payload_tvalid_int;
reg        output_udp_payload_tready_int = 0;
reg        output_udp_payload_tlast_int;
reg        output_udp_payload_tuser_int;
wire       output_udp_payload_tready_int_early;
{% for p in ports %}
assign input_{{p}}_udp_hdr_ready = input_{{p}}_udp_hdr_ready_reg;
{%- endfor %}
{% for p in ports %}
assign input_{{p}}_udp_payload_tready = input_{{p}}_udp_payload_tready_reg;
{%- endfor %}

assign output_udp_hdr_valid = output_udp_hdr_valid_reg;
assign output_eth_dest_mac = output_eth_dest_mac_reg;
assign output_eth_src_mac = output_eth_src_mac_reg;
assign output_eth_type = output_eth_type_reg;
assign output_ip_version = output_ip_version_reg;
assign output_ip_ihl = output_ip_ihl_reg;
assign output_ip_dscp = output_ip_dscp_reg;
assign output_ip_ecn = output_ip_ecn_reg;
assign output_ip_length = output_ip_length_reg;
assign output_ip_identification = output_ip_identification_reg;
assign output_ip_flags = output_ip_flags_reg;
assign output_ip_fragment_offset = output_ip_fragment_offset_reg;
assign output_ip_ttl = output_ip_ttl_reg;
assign output_ip_protocol = output_ip_protocol_reg;
assign output_ip_header_checksum = output_ip_header_checksum_reg;
assign output_ip_source_ip = output_ip_source_ip_reg;
assign output_ip_dest_ip = output_ip_dest_ip_reg;
assign output_udp_source_port = output_udp_source_port_reg;
assign output_udp_dest_port = output_udp_dest_port_reg;
assign output_udp_length = output_udp_length_reg;
assign output_udp_checksum = output_udp_checksum_reg;

// mux for start of packet detection
reg selected_input_udp_hdr_valid;
reg [47:0] selected_input_eth_dest_mac;
reg [47:0] selected_input_eth_src_mac;
reg [15:0] selected_input_eth_type;
reg [3:0]  selected_input_ip_version;
reg [3:0]  selected_input_ip_ihl;
reg [5:0]  selected_input_ip_dscp;
reg [1:0]  selected_input_ip_ecn;
reg [15:0] selected_input_ip_length;
reg [15:0] selected_input_ip_identification;
reg [2:0]  selected_input_ip_flags;
reg [12:0] selected_input_ip_fragment_offset;
reg [7:0]  selected_input_ip_ttl;
reg [7:0]  selected_input_ip_protocol;
reg [15:0] selected_input_ip_header_checksum;
reg [31:0] selected_input_ip_source_ip;
reg [31:0] selected_input_ip_dest_ip;
reg [15:0] selected_input_udp_source_port;
reg [15:0] selected_input_udp_dest_port;
reg [15:0] selected_input_udp_length;
reg [15:0] selected_input_udp_checksum;
always @* begin
    case (select)
{%- for p in ports %}
        {{w}}'d{{p}}: begin
            selected_input_udp_hdr_valid = input_{{p}}_udp_hdr_valid;
            selected_input_eth_dest_mac = input_{{p}}_eth_dest_mac;
            selected_input_eth_src_mac = input_{{p}}_eth_src_mac;
            selected_input_eth_type = input_{{p}}_eth_type;
            selected_input_ip_version = input_{{p}}_ip_version;
            selected_input_ip_ihl = input_{{p}}_ip_ihl;
            selected_input_ip_dscp = input_{{p}}_ip_dscp;
            selected_input_ip_ecn = input_{{p}}_ip_ecn;
            selected_input_ip_length = input_{{p}}_ip_length;
            selected_input_ip_identification = input_{{p}}_ip_identification;
            selected_input_ip_flags = input_{{p}}_ip_flags;
            selected_input_ip_fragment_offset = input_{{p}}_ip_fragment_offset;
            selected_input_ip_ttl = input_{{p}}_ip_ttl;
            selected_input_ip_protocol = input_{{p}}_ip_protocol;
            selected_input_ip_header_checksum = input_{{p}}_ip_header_checksum;
            selected_input_ip_source_ip = input_{{p}}_ip_source_ip;
            selected_input_ip_dest_ip = input_{{p}}_ip_dest_ip;
            selected_input_udp_source_port = input_{{p}}_udp_source_port;
            selected_input_udp_dest_port = input_{{p}}_udp_dest_port;
            selected_input_udp_length = input_{{p}}_udp_length;
            selected_input_udp_checksum = input_{{p}}_udp_checksum;
        end
{%- endfor %}
    endcase
end

// mux for incoming packet
reg [63:0] current_input_tdata;
reg [7:0] current_input_tkeep;
reg current_input_tvalid;
reg current_input_tready;
reg current_input_tlast;
reg current_input_tuser;
always @* begin
    case (select_reg)
{%- for p in ports %}
        {{w}}'d{{p}}: begin
            current_input_tdata = input_{{p}}_udp_payload_tdata;
            current_input_tkeep = input_{{p}}_udp_payload_tkeep;
            current_input_tvalid = input_{{p}}_udp_payload_tvalid;
            current_input_tready = input_{{p}}_udp_payload_tready;
            current_input_tlast = input_{{p}}_udp_payload_tlast;
            current_input_tuser = input_{{p}}_udp_payload_tuser;
        end
{%- endfor %}
    endcase
end

always @* begin
    select_next = select_reg;
    frame_next = frame_reg;
{% for p in ports %}
    input_{{p}}_udp_hdr_ready_next = input_{{p}}_udp_hdr_ready_reg & ~input_{{p}}_udp_hdr_valid;
{%- endfor %}
{% for p in ports %}
    input_{{p}}_udp_payload_tready_next = 0;
{%- endfor %}

    output_udp_hdr_valid_next = output_udp_hdr_valid_reg & ~output_udp_hdr_ready;
    output_eth_dest_mac_next = output_eth_dest_mac_reg;
    output_eth_src_mac_next = output_eth_src_mac_reg;
    output_eth_type_next = output_eth_type_reg;
    output_ip_version_next = output_ip_version_reg;
    output_ip_ihl_next = output_ip_ihl_reg;
    output_ip_dscp_next = output_ip_dscp_reg;
    output_ip_ecn_next = output_ip_ecn_reg;
    output_ip_length_next = output_ip_length_reg;
    output_ip_identification_next = output_ip_identification_reg;
    output_ip_flags_next = output_ip_flags_reg;
    output_ip_fragment_offset_next = output_ip_fragment_offset_reg;
    output_ip_ttl_next = output_ip_ttl_reg;
    output_ip_protocol_next = output_ip_protocol_reg;
    output_ip_header_checksum_next = output_ip_header_checksum_reg;
    output_ip_source_ip_next = output_ip_source_ip_reg;
    output_ip_dest_ip_next = output_ip_dest_ip_reg;
    output_udp_source_port_next = output_udp_source_port_reg;
    output_udp_dest_port_next = output_udp_dest_port_reg;
    output_udp_length_next = output_udp_length_reg;
    output_udp_checksum_next = output_udp_checksum_reg;

    if (frame_reg) begin
        if (current_input_tvalid & current_input_tready) begin
            // end of frame detection
            frame_next = ~current_input_tlast;
        end
    end else if (enable & ~output_udp_hdr_valid & selected_input_udp_hdr_valid) begin
        // start of frame, grab select value
        frame_next = 1;
        select_next = select;

        case (select_next)
{%- for p in ports %}
            {{w}}'d{{p}}: input_{{p}}_udp_hdr_ready_next = 1;
{%- endfor %}
        endcase

        output_udp_hdr_valid_next = 1;
        output_eth_dest_mac_next = selected_input_eth_dest_mac;
        output_eth_src_mac_next = selected_input_eth_src_mac;
        output_eth_type_next = selected_input_eth_type;
        output_ip_version_next = selected_input_ip_version;
        output_ip_ihl_next = selected_input_ip_ihl;
        output_ip_dscp_next = selected_input_ip_dscp;
        output_ip_ecn_next = selected_input_ip_ecn;
        output_ip_length_next = selected_input_ip_length;
        output_ip_identification_next = selected_input_ip_identification;
        output_ip_flags_next = selected_input_ip_flags;
        output_ip_fragment_offset_next = selected_input_ip_fragment_offset;
        output_ip_ttl_next = selected_input_ip_ttl;
        output_ip_protocol_next = selected_input_ip_protocol;
        output_ip_header_checksum_next = selected_input_ip_header_checksum;
        output_ip_source_ip_next = selected_input_ip_source_ip;
        output_ip_dest_ip_next = selected_input_ip_dest_ip;
        output_udp_source_port_next = selected_input_udp_source_port;
        output_udp_dest_port_next = selected_input_udp_dest_port;
        output_udp_length_next = selected_input_udp_length;
        output_udp_checksum_next = selected_input_udp_checksum;
    end

    // generate ready signal on selected port
    case (select_next)
{%- for p in ports %}
        {{w}}'d{{p}}: input_{{p}}_udp_payload_tready_next = output_udp_payload_tready_int_early & frame_next;
{%- endfor %}
    endcase

    // pass through selected packet data
    output_udp_payload_tdata_int = current_input_tdata;
    output_udp_payload_tkeep_int = current_input_tkeep;
    output_udp_payload_tvalid_int = current_input_tvalid & current_input_tready & frame_reg;
    output_udp_payload_tlast_int = current_input_tlast;
    output_udp_payload_tuser_int = current_input_tuser;
end

always @(posedge clk or posedge rst) begin
    if (rst) begin
        select_reg <= 0;
        frame_reg <= 0;
{%- for p in ports %}
        input_{{p}}_udp_hdr_ready_reg <= 0;
{%- endfor %}
{%- for p in ports %}
        input_{{p}}_udp_payload_tready_reg <= 0;
{%- endfor %}
        output_udp_hdr_valid_reg <= 0;
        output_eth_dest_mac_reg <= 0;
        output_eth_src_mac_reg <= 0;
        output_eth_type_reg <= 0;
        output_ip_version_reg <= 0;
        output_ip_ihl_reg <= 0;
        output_ip_dscp_reg <= 0;
        output_ip_ecn_reg <= 0;
        output_ip_length_reg <= 0;
        output_ip_identification_reg <= 0;
        output_ip_flags_reg <= 0;
        output_ip_fragment_offset_reg <= 0;
        output_ip_ttl_reg <= 0;
        output_ip_protocol_reg <= 0;
        output_ip_header_checksum_reg <= 0;
        output_ip_source_ip_reg <= 0;
        output_ip_dest_ip_reg <= 0;
        output_udp_source_port_reg <= 0;
        output_udp_dest_port_reg <= 0;
        output_udp_length_reg <= 0;
        output_udp_checksum_reg <= 0;
    end else begin
        select_reg <= select_next;
        frame_reg <= frame_next;
{%- for p in ports %}
        input_{{p}}_udp_hdr_ready_reg <= input_{{p}}_udp_hdr_ready_next;
{%- endfor %}
{%- for p in ports %}
        input_{{p}}_udp_payload_tready_reg <= input_{{p}}_udp_payload_tready_next;
{%- endfor %}
        output_udp_hdr_valid_reg <= output_udp_hdr_valid_next;
        output_eth_dest_mac_reg <= output_eth_dest_mac_next;
        output_eth_src_mac_reg <= output_eth_src_mac_next;
        output_eth_type_reg <= output_eth_type_next;
        output_ip_version_reg <= output_ip_version_next;
        output_ip_ihl_reg <= output_ip_ihl_next;
        output_ip_dscp_reg <= output_ip_dscp_next;
        output_ip_ecn_reg <= output_ip_ecn_next;
        output_ip_length_reg <= output_ip_length_next;
        output_ip_identification_reg <= output_ip_identification_next;
        output_ip_flags_reg <= output_ip_flags_next;
        output_ip_fragment_offset_reg <= output_ip_fragment_offset_next;
        output_ip_ttl_reg <= output_ip_ttl_next;
        output_ip_protocol_reg <= output_ip_protocol_next;
        output_ip_header_checksum_reg <= output_ip_header_checksum_next;
        output_ip_source_ip_reg <= output_ip_source_ip_next;
        output_ip_dest_ip_reg <= output_ip_dest_ip_next;
        output_udp_source_port_reg <= output_udp_source_port_next;
        output_udp_dest_port_reg <= output_udp_dest_port_next;
        output_udp_length_reg <= output_udp_length_next;
        output_udp_checksum_reg <= output_udp_checksum_next;
    end
end

// output datapath logic
reg [63:0] output_udp_payload_tdata_reg = 0;
reg [7:0]  output_udp_payload_tkeep_reg = 0;
reg        output_udp_payload_tvalid_reg = 0;
reg        output_udp_payload_tlast_reg = 0;
reg        output_udp_payload_tuser_reg = 0;

reg [63:0] temp_udp_payload_tdata_reg = 0;
reg [7:0]  temp_udp_payload_tkeep_reg = 0;
reg        temp_udp_payload_tvalid_reg = 0;
reg        temp_udp_payload_tlast_reg = 0;
reg        temp_udp_payload_tuser_reg = 0;

assign output_udp_payload_tdata = output_udp_payload_tdata_reg;
assign output_udp_payload_tkeep = output_udp_payload_tkeep_reg;
assign output_udp_payload_tvalid = output_udp_payload_tvalid_reg;
assign output_udp_payload_tlast = output_udp_payload_tlast_reg;
assign output_udp_payload_tuser = output_udp_payload_tuser_reg;

// enable ready input next cycle if output is ready or if there is space in both output registers or if there is space in the temp register that will not be filled next cycle
assign output_udp_payload_tready_int_early = output_udp_payload_tready | (~temp_udp_payload_tvalid_reg & ~output_udp_payload_tvalid_reg) | (~temp_udp_payload_tvalid_reg & ~output_udp_payload_tvalid_int);

always @(posedge clk or posedge rst) begin
    if (rst) begin
        output_udp_payload_tdata_reg <= 0;
        output_udp_payload_tkeep_reg <= 0;
        output_udp_payload_tvalid_reg <= 0;
        output_udp_payload_tlast_reg <= 0;
        output_udp_payload_tuser_reg <= 0;
        output_udp_payload_tready_int <= 0;
        temp_udp_payload_tdata_reg <= 0;
        temp_udp_payload_tkeep_reg <= 0;
        temp_udp_payload_tvalid_reg <= 0;
        temp_udp_payload_tlast_reg <= 0;
        temp_udp_payload_tuser_reg <= 0;
    end else begin
        // transfer sink ready state to source
        output_udp_payload_tready_int <= output_udp_payload_tready_int_early;

        if (output_udp_payload_tready_int) begin
            // input is ready
            if (output_udp_payload_tready | ~output_udp_payload_tvalid_reg) begin
                // output is ready or currently not valid, transfer data to output
                output_udp_payload_tdata_reg <= output_udp_payload_tdata_int;
                output_udp_payload_tkeep_reg <= output_udp_payload_tkeep_int;
                output_udp_payload_tvalid_reg <= output_udp_payload_tvalid_int;
                output_udp_payload_tlast_reg <= output_udp_payload_tlast_int;
                output_udp_payload_tuser_reg <= output_udp_payload_tuser_int;
            end else begin
                // output is not ready, store input in temp
                temp_udp_payload_tdata_reg <= output_udp_payload_tdata_int;
                temp_udp_payload_tkeep_reg <= output_udp_payload_tkeep_int;
                temp_udp_payload_tvalid_reg <= output_udp_payload_tvalid_int;
                temp_udp_payload_tlast_reg <= output_udp_payload_tlast_int;
                temp_udp_payload_tuser_reg <= output_udp_payload_tuser_int;
            end
        end else if (output_udp_payload_tready) begin
            // input is not ready, but output is ready
            output_udp_payload_tdata_reg <= temp_udp_payload_tdata_reg;
            output_udp_payload_tkeep_reg <= temp_udp_payload_tkeep_reg;
            output_udp_payload_tvalid_reg <= temp_udp_payload_tvalid_reg;
            output_udp_payload_tlast_reg <= temp_udp_payload_tlast_reg;
            output_udp_payload_tuser_reg <= temp_udp_payload_tuser_reg;
            temp_udp_payload_tdata_reg <= 0;
            temp_udp_payload_tkeep_reg <= 0;
            temp_udp_payload_tvalid_reg <= 0;
            temp_udp_payload_tlast_reg <= 0;
            temp_udp_payload_tuser_reg <= 0;
        end
    end
end

endmodule

""")
    
    out_file.write(t.render(
        n=ports,
        w=select_width,
        name=name,
        ports=range(ports)
    ))
    
    print("Done")

if __name__ == "__main__":
    sys.exit(main())

