from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os

import logging

log = logging.getLogger(__name__)

from .db import SettingsDb
from ..ssp_dicts import Dicts
from ..helper import SspError
from ..pkg_clients import PkgClientList


class Settings(object):

    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self):
        # waiting time
        self.rx_max_wait_time = None
        # oceanographic data sources
        self.ssp_extension_source = None
        self.ssp_salinity_source = None
        self.ssp_temp_sal_source = None
        self.sis_server_source = None
        self.woa_path = None
        # processing
        self.ssp_up_or_down = None
        # user export settings
        self.user_append_caris_file = None
        self.user_export_prompt_filename = None
        self.auto_export_on_send = None
        # server settings
        self.server_append_caris_file = None
        self.auto_export_on_server_send = None
        self.server_apply_surface_sound_speed = None
        # sis settings
        self.km_listen_port = None
        self.km_listen_timeout = None
        self.sis_auto_apply_manual_casts = None
        # Sippican settings
        self.sippican_listen_port = None
        self.sippican_listen_timeout = None
        # MVP settings
        self.mvp_ip_address = None
        self.mvp_listen_port = None
        self.mvp_listen_timeout = None
        self.mvp_transmission_protocol = None
        self.mvp_format = None
        self.mvp_winch_port = None
        self.mvp_fish_port = None
        self.mvp_nav_port = None
        self.mvp_system_port = None
        self.mvp_sw_version = None
        self.mvp_instrument = None
        self.mvp_instrument_id = None

        self.client_list = PkgClientList()

    def load_settings_from_db(self):
        db = SettingsDb()
        log.debug("Settings name: %s" % db.settings_name)
        self.rx_max_wait_time = db.rx_max_wait_time
        self.ssp_extension_source = Dicts.extension_sources[db.ssp_extension_source]
        self.ssp_salinity_source = Dicts.salinity_sources[db.ssp_salinity_source]
        self.ssp_temp_sal_source = Dicts.temp_sal_sources[db.ssp_temp_sal_source]
        self.sis_server_source = Dicts.sis_server_sources[db.sis_server_source]
        self.woa_path = db.woa_path
        self.ssp_up_or_down = Dicts.ssp_directions[db.ssp_up_or_down]
        self.user_append_caris_file = db.user_append_caris_file
        self.user_export_prompt_filename = db.user_export_prompt_filename
        self.auto_export_on_send = db.auto_export_on_send
        self.server_append_caris_file = db.server_append_caris_file
        self.auto_export_on_server_send = db.auto_export_on_server_send
        self.server_apply_surface_sound_speed = db.server_apply_surface_sound_speed
        self.km_listen_port = db.km_listen_port
        self.km_listen_timeout = db.km_listen_timeout
        self.sis_auto_apply_manual_casts = db.sis_auto_apply_manual_casts
        self.sippican_listen_port = db.sippican_listen_port
        self.sippican_listen_timeout = db.sippican_listen_timeout
        self.mvp_ip_address = db.mvp_ip_address
        self.mvp_listen_port = db.mvp_listen_port
        self.mvp_listen_timeout = db.mvp_listen_timeout
        self.mvp_transmission_protocol = db.mvp_transmission_protocol
        self.mvp_format = db.mvp_format
        self.mvp_winch_port = db.mvp_winch_port
        self.mvp_fish_port = db.mvp_fish_port
        self.mvp_nav_port = db.mvp_nav_port
        self.mvp_system_port = db.mvp_system_port
        self.mvp_sw_version = db.mvp_sw_version
        self.mvp_instrument = db.mvp_instrument
        self.mvp_instrument_id = db.mvp_instrument_id

        for client in db.client_list:
            client_string = "\"%s\":%s:%s:%s" % (client[0], client[1], client[2], client[3])
            # print(client_string)
            self.client_list.add_client(client_string)
        db.close()

    @classmethod
    def active_settings_id(cls):
        db = SettingsDb()
        settings_id = db.active_settings_id
        db.close()
        return settings_id

    def __str__(self):
        output = " # Settings (timestamp: %s) #\n" % datetime.datetime.now().isoformat()

        output += "\n > Waiting time: rx_max_wait_time:  %s\n" % self.rx_max_wait_time

        output += "\n > Oceanographic data sources\n"
        try:
            output += "   - ssp_extension_source:  %s >> %s\n" \
                      % (self.ssp_extension_source,
                         Dicts.first_match(Dicts.extension_sources, self.ssp_extension_source))
        except SspError:
            output += "   - ssp_extension_source:  %s\n" % self.ssp_extension_source

        try:
            output += "   - ssp_salinity_source:  %s >> %s\n" \
                      % (self.ssp_salinity_source,
                         Dicts.first_match(Dicts.salinity_sources, self.ssp_salinity_source))
        except SspError:
            output += "   - ssp_salinity_source:  %s\n" % self.ssp_salinity_source

        try:
            output += "   - ssp_temp_sal_source:  %s >> %s\n" \
                      % (self.ssp_temp_sal_source,
                         Dicts.first_match(Dicts.temp_sal_sources, self.ssp_temp_sal_source))
        except SspError:
            output += "   - ssp_temp_sal_source:  %s\n" % self.ssp_temp_sal_source

        try:
            output += "   - sis_server_source:  %s >> %s\n" \
                      % (self.sis_server_source,
                         Dicts.first_match(Dicts.sis_server_sources, self.sis_server_source))
        except SspError:
            output += "   - sis_server_source:  %s\n" % self.sis_server_source

        output += "   - woa_path:  %s\n" % self.woa_path

        try:
            output += "\n > Processing: ssp_up_or_down:  %s >> %s\n" \
                      % (self.ssp_up_or_down, Dicts.first_match(Dicts.ssp_directions, self.ssp_up_or_down))
        except SspError:
            output += "\n > Processing: ssp_up_or_down:  %s\n" % self.ssp_up_or_down

        output += "\n > User\n"
        output += "   - user_append_caris_file:  %s\n" % self.user_append_caris_file
        output += "   - user_export_prompt_filename:  %s\n" % self.user_export_prompt_filename
        output += "   - auto_export_on_send:  %s\n" % self.auto_export_on_send

        output += "\n > Server\n"
        output += "   - server_append_caris_file: %s\n" % self.server_append_caris_file
        output += "   - auto_export_on_server_send: %s\n" % self.auto_export_on_server_send
        output += "   - server_apply_surface_sound_speed: %s\n" % self.server_apply_surface_sound_speed

        output += "\n > SIS settings: "
        output += "km_listen_port: %s, " % self.km_listen_port
        output += "km_listen_timeout: %s, " % self.km_listen_timeout
        output += "sis_auto_apply_manual_casts: %s\n" % self.sis_auto_apply_manual_casts

        output += "\n > Sippican settings: "
        output += "sippican_listen_port: %s, " % self.sippican_listen_port
        output += "sippican_listen_timeout: %s\n" % self.sippican_listen_timeout

        output += "\n > MVP settings\n"
        output += "   - mvp_ip_address: %s, mvp_listen_port: %s\n" % (self.mvp_ip_address, self.mvp_listen_port)
        output += "   - mvp_listen_timeout: %s\n" % self.mvp_listen_timeout
        output += "   - mvp_transmission_protocol: %s\n" % self.mvp_transmission_protocol
        output += "   - mvp_format: %s\n" % self.mvp_format
        output += "   - mvp_winch_port: %s, mvp_fish_port: %s, mvp_nav_port: %s, mvp_system_port: %s\n" \
                  % (self.mvp_winch_port, self.mvp_fish_port, self.mvp_nav_port, self.mvp_system_port)
        output += "   - mvp_sw_version: %s\n" % self.mvp_sw_version
        output += "   - mvp_instrument: %s\n" % self.mvp_instrument
        output += "   - mvp_instrument_id: %s\n" % self.mvp_instrument_id

        output += "\n > Clients\n"
        for cln in self.client_list.clients:
            output += "   - %s %s:%s %s [%s]\n" % (cln.name, cln.IP, cln.port, cln.protocol, cln.alive)

        return output

