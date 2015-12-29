from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sqlite3
import logging

log = logging.getLogger(__name__)

from hydroffice.base.base_objects import BaseDbObject
from ..helper import Helper, SspError


class DbSettingsError(SspError):
    """ Error raised for db issues """
    def __init__(self, message, *args):
        self.message = message
        super(DbSettingsError, self).__init__(message, *args)


class SettingsDb(BaseDbObject):
    """ Class that stores SSP settings in a SQLite db """

    def __init__(self, db_path=None):
        if not db_path:
            db_path = os.path.join(Helper.default_projects_folder(), "__settings__.db")
        super(SettingsDb, self).__init__(db_path=db_path)
        self.reconnect_or_create()
        self.check_default_profile()

    def build_tables(self):
        if not self.conn:
            log.error("Missing db connection")
            return False

        try:
            with self.conn:
                if self.conn.execute(""" PRAGMA foreign_keys """):
                    log.info("foreign keys active")
                else:
                    log.error("foreign keys not active")
                    return False
                self.conn.execute(GENERAL_CREATION_STRING)
                self.conn.execute(CLIENT_LIST_CREATION_STRING)
                self.conn.execute(SETTINGS_VIEW_CREATION_STRING)
            return True

        except sqlite3.Error as e:
            log.error("during building tables, %s: %s" % (type(e), e))
            return False

    # --- profile stuff
    def check_default_profile(self):
        """ Check for the presence of default settings, creating them if missing. """
        default_settings = "default"
        if not self.profile_exists(default_settings):
            self.add_profile(profile_name=default_settings)
            self.activate_profile(profile_name=default_settings)

    def profile_exists(self, profile_name):
        """ Check if the passed profile exists

        Args:
            profile_name:          The name of the profile
        Returns:
            bool:                   True if present
        """
        try:
            ret = self.conn.execute(""" SELECT COUNT(id) FROM general WHERE profile_name=? """,
                                    (profile_name,)).fetchone()
            # log.info("found %s settings named %s" % (ret[0], profile_name))
            if ret[0] == 0:
                return False
            else:
                return True
        except sqlite3.Error as e:
            raise DbSettingsError("%s: %s" % (type(e), e))

    def add_profile(self, profile_name):
        """ Add setting with passed name and default values.

        Args:
            profile_name:              The name of the new settings
        """
        with self.conn:
            try:
                # create a default settings record
                self.conn.execute(""" INSERT INTO general (profile_name) VALUES(?) """, (profile_name,))
                # log.info("inserted %s settings with default values" % profile_name)

                # retrieve settings id
                ret = self.conn.execute(""" SELECT id FROM general WHERE profile_name=? """,
                                        (profile_name,)).fetchone()
                # log.info("%s settings id: %s" % (profile_name, ret[0]))

                # add default client list
                self.conn.execute(""" INSERT INTO client_list (profile_id) VALUES(?) """, (ret[0], ))
                # log.info("inserted %s settings values" % profile_name)

            except sqlite3.Error as e:
                log.error("%s: %s" % (type(e), e))
                return False

    def delete_profile(self, profile_name):
        """ Delete a profile (if not active).

        Args:
            profile_name:              The name of the new settings
        """
        with self.conn:
            try:
                # check if active
                ret = self.conn.execute(""" SELECT profile_status FROM general WHERE profile_name=? """, (profile_name,)).fetchone()
                # log.info("%s settings status: %s" % (profile_name, ret))
                if ret == "active":
                    raise DbSettingsError("Attempt to delete active profile (%s)" % profile_name)

                # create a default settings record
                self.conn.execute(""" DELETE FROM general WHERE profile_name=? """, (profile_name,))
                # log.info("deleted profile: %s" % profile_name)

            except sqlite3.Error as e:
                log.error("%s: %s" % (type(e), e))
                return False

    def activate_profile(self, profile_name):
        """ Activate a profile, if it exists

        Args:
            profile_name:           The name of the profile to activate
        Returns:
            bool:                   True if the profile was activated
        """
        if not self.profile_exists(profile_name):
            return False

        with self.conn:
            try:
                # set all the values to inactive
                self.conn.execute(""" UPDATE general SET profile_status="inactive" """)
                # set active just the passed profile
                self.conn.execute(""" UPDATE general SET profile_status="active" WHERE profile_name=? """, (profile_name, ))
                # log.info("activated profile: %s" % profile_name)
            except sqlite3.Error as e:
                log.error("%s: %s" % (type(e), e))
                return False

    @property
    def active_profile_id(self):
        """ Retrieve the active settings id """
        ret = self.conn.execute(""" SELECT id FROM general WHERE profile_status="active" """).fetchone()
        return ret[0]

    @property
    def active_profile_name(self):
        """ retrieve the active settings name """
        ret = self.conn.execute(""" SELECT profile_name FROM general WHERE profile_status="active" """).fetchone()
        return ret[0]

   # --- active settings name
    @property
    def active_profile_name(self):
        ret = self.conn.execute(""" SELECT profile_name FROM general WHERE id=? """,
                                (self.active_profile_id,)).fetchone()
        log.info("Settings name: %s" % ret[0])
        return ret[0]

    # --- clients list
    @property
    def client_list(self):
        ret = self.conn.execute(""" SELECT id, name, ip, port, protocol FROM client_list WHERE profile_id=? """,
                                (self.active_profile_id,)).fetchall()
        log.info("SSP clients: %s" % len(ret))
        return ret

    def client_exists(self, client_name):
        """ Check if the passed profile exists

        Args:
            client_name:            The name of the client
        Returns:
            bool:                   True if present
        """
        try:
            ret = self.conn.execute(""" SELECT COUNT(id) FROM client_list WHERE name=? """,
                                    (client_name,)).fetchone()
            # log.info("found %s clients named %s" % (ret[0], client_name))
            if ret[0] == 0:
                return False
            else:
                return True
        except sqlite3.Error as e:
            raise DbSettingsError("%s: %s" % (type(e), e))

    def add_client(self, client_name, client_ip="127.0.0.1", client_port=4001, client_protocol="SIS"):
        """ Add client with passed name and default values.

        Args:
            client_name:              The name of the new client
            client_ip:                The client IP
            client_port:              The client port
            client_protocol:          The client protocol
        """
        with self.conn:
            try:
                self.conn.execute(""" INSERT INTO client_list (profile_id, name, ip, port, protocol)
                                                  VALUES(?, ?, ?, ?, ?) """,
                                  (self.active_profile_id, client_name, client_ip, client_port, client_protocol))
                # log.info("inserted %s client values" % client_name, client_ip, client_port, client_protocol)

            except sqlite3.Error as e:
                log.error("%s: %s" % (type(e), e))
                return False

    def delete_client(self, client_name):
        """ Delete a client.

        Args:
            client_name:              The name of the new client
        """
        with self.conn:
            try:
                self.conn.execute(""" DELETE FROM client_list WHERE name=? """, (client_name,))
                # log.info("deleted client: %s" % client_name)

            except sqlite3.Error as e:
                log.error("%s: %s" % (type(e), e))
                return False

    # --- profiles list
    @property
    def profiles_list(self):
        ret = self.conn.execute(""" SELECT id, profile_name, profile_status FROM general """).fetchall()
        log.info("Profiles list: %s" % len(ret))
        return ret

    # --- templates
    def _getter_int(self, attrib):
        r = self.conn.execute(""" SELECT """ + attrib + """ FROM general WHERE id=? """,
                              (self.active_profile_id,)).fetchone()
        log.info("%s = %d" % (attrib, r[0]))
        return r[0]

    def _setter_int(self, attrib, value):
        with self.conn:
            try:
                self.conn.execute(""" UPDATE general SET """ + attrib + """=? WHERE id=? """,
                                  (value, self.active_profile_id,))
            except sqlite3.Error as e:
                log.error("%s: %s" % (type(e), e))
        log.info("%s = %d" % (attrib, value))

    def _getter_str(self, attrib):
        r = self.conn.execute(""" SELECT """ + attrib + """ FROM general WHERE id=? """,
                              (self.active_profile_id,)).fetchone()
        log.info("%s = %s" % (attrib, r[0]))
        return r[0]

    def _setter_str(self, attrib, value):
        with self.conn:
            try:
                self.conn.execute(""" UPDATE general SET """ + attrib + """=? WHERE id=? """,
                                  (value, self.active_profile_id,))
            except sqlite3.Error as e:
                log.error("%s: %s" % (type(e), e))
        log.info("%s = %s" % (attrib, value))

    def _getter_bool(self, attrib):
        r = self.conn.execute(""" SELECT """ + attrib + """ FROM general WHERE id=? """,
                              (self.active_profile_id,)).fetchone()
        log.info("%s = %s" % (attrib, r[0]))
        return r[0] == "True"

    def _setter_bool(self, attrib, value):
        with self.conn:
            try:
                self.conn.execute(""" UPDATE general SET """ + attrib + """=? WHERE id=? """,
                                  (value, self.active_profile_id,))
            except sqlite3.Error as e:
                log.error("%s: %s" % (type(e), e))
        log.info("%s = %s" % (attrib, value))

    # --- rx_max_wait_time
    @property
    def rx_max_wait_time(self):
        return self._getter_int("rx_max_wait_time")

    @rx_max_wait_time.setter
    def rx_max_wait_time(self, value):
        self._setter_int("rx_max_wait_time", value)

    # --- ssp_extension_source
    @property
    def ssp_extension_source(self):
        return self._getter_str("ssp_extension_source")

    @ssp_extension_source.setter
    def ssp_extension_source(self, value):
        self._setter_str("ssp_extension_source", value)

    # --- ssp_salinity_source
    @property
    def ssp_salinity_source(self):
        return self._getter_str("ssp_salinity_source")

    @ssp_salinity_source.setter
    def ssp_salinity_source(self, value):
        self._setter_str("ssp_salinity_source", value)

    # --- ssp_temp_sal_source
    @property
    def ssp_temp_sal_source(self):
        return self._getter_str("ssp_temp_sal_source")

    @ssp_temp_sal_source.setter
    def ssp_temp_sal_source(self, value):
        self._setter_str("ssp_temp_sal_source", value)

    # --- ssp_temp_sal_source
    @property
    def sis_server_source(self):
        return self._getter_str("sis_server_source")

    @sis_server_source.setter
    def sis_server_source(self, value):
        self._setter_str("sis_server_source", value)

    # --- woa_path
    @property
    def woa_path(self):
        return self._getter_str("woa_path")

    @woa_path.setter
    def woa_path(self, value):
        self._setter_str("woa_path", value)

    # --- ssp_up_or_down
    @property
    def ssp_up_or_down(self):
        return self._getter_str("ssp_up_or_down")

    @ssp_up_or_down.setter
    def ssp_up_or_down(self, value):
        self._setter_str("ssp_up_or_down", value)

    # --- user_append_caris_file
    @property
    def user_append_caris_file(self):
        return self._getter_bool("user_append_caris_file")

    @user_append_caris_file.setter
    def user_append_caris_file(self, value):
        self._setter_str("user_append_caris_file", value)

    # --- user_export_prompt_filename
    @property
    def user_export_prompt_filename(self):
        return self._getter_bool("user_export_prompt_filename")

    @user_export_prompt_filename.setter
    def user_export_prompt_filename(self, value):
        self._setter_str("user_export_prompt_filename", value)

    # --- auto_export_on_send
    @property
    def auto_export_on_send(self):
        return self._getter_bool("auto_export_on_send")

    @auto_export_on_send.setter
    def auto_export_on_send(self, value):
        self._setter_str("auto_export_on_send", value)

    # --- server_append_caris_file
    @property
    def server_append_caris_file(self):
        return self._getter_bool("server_append_caris_file")

    @server_append_caris_file.setter
    def server_append_caris_file(self, value):
        self._setter_str("server_append_caris_file", value)

    # --- auto_export_on_server_send
    @property
    def auto_export_on_server_send(self):
        return self._getter_bool("auto_export_on_server_send")

    @auto_export_on_server_send.setter
    def auto_export_on_server_send(self, value):
        self._setter_str("auto_export_on_server_send", value)

    # --- server_apply_surface_sound_speed
    @property
    def server_apply_surface_sound_speed(self):
        return self._getter_bool("server_apply_surface_sound_speed")

    @server_apply_surface_sound_speed.setter
    def server_apply_surface_sound_speed(self, value):
        self._setter_str("server_apply_surface_sound_speed", value)

    # --- km_listen_port
    @property
    def km_listen_port(self):
        return self._getter_int("km_listen_port")

    @km_listen_port.setter
    def km_listen_port(self, value):
        self._setter_int("km_listen_port", value)

    # --- km_listen_timeout
    @property
    def km_listen_timeout(self):
        return self._getter_int("km_listen_timeout")

    @km_listen_timeout.setter
    def km_listen_timeout(self, value):
        self._setter_int("km_listen_timeout", value)

    # --- sis_auto_apply_manual_casts
    @property
    def sis_auto_apply_manual_casts(self):
        return self._getter_bool("sis_auto_apply_manual_casts")

    @sis_auto_apply_manual_casts.setter
    def sis_auto_apply_manual_casts(self, value):
        self._setter_bool("sis_auto_apply_manual_casts", value)

    # --- sippican_listen_port
    @property
    def sippican_listen_port(self):
        return self._getter_int("sippican_listen_port")

    @sippican_listen_port.setter
    def sippican_listen_port(self, value):
        self._setter_int("sippican_listen_port", value)

    # --- sippican_listen_timeout
    @property
    def sippican_listen_timeout(self):
        return self._getter_int("sippican_listen_timeout")

    @sippican_listen_timeout.setter
    def sippican_listen_timeout(self, value):
        self._setter_int("sippican_listen_timeout", value)

    # --- mvp_ip_address
    @property
    def mvp_ip_address(self):
        return self._getter_str("mvp_ip_address")

    @mvp_ip_address.setter
    def mvp_ip_address(self, value):
        self._setter_str("mvp_ip_address", value)

    # --- mvp_listen_port
    @property
    def mvp_listen_port(self):
        return self._getter_int("mvp_listen_port")

    @mvp_listen_port.setter
    def mvp_listen_port(self, value):
        self._setter_int("mvp_listen_port", value)

    # --- mvp_listen_timeout
    @property
    def mvp_listen_timeout(self):
        return self._getter_int("mvp_listen_timeout")

    @mvp_listen_timeout.setter
    def mvp_listen_timeout(self, value):
        self._setter_int("mvp_listen_timeout", value)

    # --- mvp_transmission_protocol
    @property
    def mvp_transmission_protocol(self):
        return self._getter_str("mvp_transmission_protocol")

    @mvp_transmission_protocol.setter
    def mvp_transmission_protocol(self, value):
        self._setter_str("mvp_transmission_protocol", value)

    # --- mvp_format
    @property
    def mvp_format(self):
        return self._getter_str("mvp_format")

    @mvp_format.setter
    def mvp_format(self, value):
        self._setter_str("mvp_format", value)

    # --- mvp_winch_port
    @property
    def mvp_winch_port(self):
        return self._getter_int("mvp_winch_port")

    @mvp_winch_port.setter
    def mvp_winch_port(self, value):
        self._setter_int("mvp_winch_port", value)

    # --- mvp_fish_port
    @property
    def mvp_fish_port(self):
        return self._getter_int("mvp_fish_port")

    @mvp_fish_port.setter
    def mvp_fish_port(self, value):
        self._setter_int("mvp_fish_port", value)

    # --- mvp_nav_port
    @property
    def mvp_nav_port(self):
        return self._getter_int("mvp_nav_port")

    @mvp_nav_port.setter
    def mvp_nav_port(self, value):
        self._setter_int("mvp_nav_port", value)

    # --- mvp_system_port
    @property
    def mvp_system_port(self):
        return self._getter_int("mvp_system_port")

    @mvp_system_port.setter
    def mvp_system_port(self, value):
        self._setter_int("mvp_system_port", value)

    # --- mvp_sw_version
    @property
    def mvp_sw_version(self):
        return self._getter_str("mvp_sw_version")

    @mvp_sw_version.setter
    def mvp_sw_version(self, value):
        self._setter_str("mvp_sw_version", value)

    # --- mvp_instrument
    @property
    def mvp_instrument(self):
        return self._getter_str("mvp_instrument")

    @mvp_instrument.setter
    def mvp_instrument(self, value):
        self._setter_str("mvp_instrument", value)

    # --- mvp_instrument_id
    @property
    def mvp_instrument_id(self):
        return self._getter_str("mvp_instrument_id")

    @mvp_instrument_id.setter
    def mvp_instrument_id(self, value):
        self._setter_str("mvp_instrument_id", value)

GENERAL_CREATION_STRING = """ CREATE TABLE IF NOT EXISTS general(
     id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
     profile_name text NOT NULL UNIQUE DEFAULT "default",
     profile_status text NOT NULL DEFAULT "inactive",
     rx_max_wait_time integer NOT NULL DEFAULT 30,
     ssp_extension_source text NOT NULL DEFAULT "WOA09",
     ssp_salinity_source text NOT NULL DEFAULT "WOA09",
     ssp_temp_sal_source text NOT NULL DEFAULT "WOA09",
     sis_server_source text NOT NULL DEFAULT "WOA09",
     woa_path text,
     ssp_up_or_down text NOT NULL DEFAULT "down",
     auto_export_on_send text NOT NULL DEFAULT "False",
     auto_export_on_server_send text NOT NULL DEFAULT "True",
     user_export_prompt_filename text NOT NULL DEFAULT "False",
     user_append_caris_file text NOT NULL DEFAULT "False",
     server_append_caris_file text NOT NULL DEFAULT "False",
     km_listen_port integer NOT NULL DEFAULT 26103,
     km_listen_timeout integer NOT NULL DEFAULT 1,
     sis_auto_apply_manual_casts text NOT NULL DEFAULT "True",
     server_apply_surface_sound_speed text NOT NULL DEFAULT "True",
     sippican_listen_port integer NOT NULL DEFAULT 2002,
     sippican_listen_timeout integer NOT NULL DEFAULT 1,
     mvp_ip_address text NOT NULL DEFAULT "127.0.0.1",
     mvp_listen_port integer NOT NULL DEFAULT 2006,
     mvp_listen_timeout integer NOT NULL DEFAULT 1,
     mvp_transmission_protocol text NOT NULL DEFAULT "NAVO_ISS60",
     mvp_format text NOT NULL DEFAULT "S12",
     mvp_winch_port integer NOT NULL DEFAULT 3601,
     mvp_fish_port integer NOT NULL DEFAULT 3602,
     mvp_nav_port integer NOT NULL DEFAULT 3603,
     mvp_system_port integer NOT NULL DEFAULT 3604,
     mvp_sw_version text NOT NULL DEFAULT "2.47",
     mvp_instrument_id text NOT NULL DEFAULT "M",
     mvp_instrument text NOT NULL DEFAULT "AML_uSVPT",
     /* Checks */
     CHECK (profile_status IN ("active", "inactive")),
     CHECK (rx_max_wait_time > 0),
     CHECK (ssp_extension_source IN ("RTOFS", "WOA09", "WOA13")),
     CHECK (ssp_salinity_source IN ("RTOFS", "WOA09", "WOA13")),
     CHECK (ssp_temp_sal_source IN ("RTOFS", "WOA09", "WOA13")),
     CHECK (sis_server_source IN ("RTOFS", "WOA09", "WOA13")),
     CHECK (ssp_up_or_down IN ("down", "up")),
     CHECK (auto_export_on_send IN ("True", "False")),
     CHECK (auto_export_on_server_send IN ("True", "False")),
     CHECK (user_export_prompt_filename IN ("True", "False")),
     CHECK (user_append_caris_file IN ("True", "False")),
     CHECK (server_append_caris_file IN ("True", "False")),
     CHECK (km_listen_port > 0),
     CHECK (km_listen_timeout > 0),
     CHECK (sis_auto_apply_manual_casts IN ("True", "False")),
     CHECK (server_apply_surface_sound_speed IN ("True", "False")),
     CHECK (sippican_listen_port > 0),
     CHECK (sippican_listen_timeout > 0),
     CHECK (mvp_listen_port > 0),
     CHECK (mvp_listen_timeout > 0),
     CHECK (mvp_transmission_protocol IN ("NAVO_ISS60", "UNDEFINED")),
     CHECK (mvp_format IN ("S12", "CALC", "ASVP")),
     CHECK (mvp_instrument IN ("AML_uSVP", "AML_uSVPT", "AML_Smart_SVP", "AML_uCTD", "AML_uCTD+", "Valeport_SVPT", "SBE_911+", "SBE_49"))
     ) """

CLIENT_LIST_CREATION_STRING = """ CREATE TABLE IF NOT EXISTS client_list(
     id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
     profile_id INTEGER NOT NULL,
     name text NOT NULL DEFAULT "Local test",
     ip text NOT NULL DEFAULT "127.0.0.1",
     port integer NOT NULL DEFAULT 4001,
     protocol text NOT NULL DEFAULT "SIS",
     CONSTRAINT profile_id_fk
     FOREIGN KEY(profile_id) REFERENCES general(id)
     ON DELETE CASCADE,
     /* Checks */
     CHECK (port > 0),
     CHECK (protocol IN ("SIS", "HYPACK", "PDS2000", "QINSY"))
     ) """

SETTINGS_VIEW_CREATION_STRING = """ CREATE VIEW IF NOT EXISTS settings_view AS
    SELECT * FROM general g
    LEFT OUTER JOIN client_list c ON g.id=c.profile_id """