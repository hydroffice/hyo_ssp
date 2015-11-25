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
        # allow users initialize misc. arguments as any other builtin Error
        super(DbSettingsError, self).__init__(message, *args)


class SettingsDb(BaseDbObject):
    """ Class that stores SSP settings in a SQLite db """

    def __init__(self, db_path=None):
        if not db_path:
            db_path = os.path.join(Helper.default_projects_folder(), "__settings__.db")
        super(SettingsDb, self).__init__(db_path=db_path)

        self.reconnect_or_create()
        self.check_default_settings()

    def build_tables(self):
        if not self.conn:
            log.error("Missing db connection")
            return False

        try:
            with self.conn:
                if self.conn.execute("""
                                     PRAGMA foreign_keys
                                     """):
                    log.info("foreign keys active")
                else:
                    log.error("foreign keys not active")
                    return False

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS general(
                                     id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                                     settings_name text NOT NULL UNIQUE DEFAULT "default",
                                     settings_status text NOT NULL DEFAULT "active",
                                     ssp_extension_source text NOT NULL DEFAULT "WOA09",
                                     ssp_salinity_source text NOT NULL DEFAULT "WOA09",
                                     ssp_temp_sal_source text NOT NULL DEFAULT "WOA09",
                                     sis_server_source text NOT NULL DEFAULT "WOA09",
                                     woa_path text,
                                     ssp_up_or_down text NOT NULL DEFAULT "downcast",
                                     auto_export_on_send text NOT NULL DEFAULT "False",
                                     auto_export_on_server_send text NOT NULL DEFAULT "True",
                                     user_export_prompt_filename text NOT NULL DEFAULT "False",
                                     user_append_caris_file text NOT NULL DEFAULT "False",
                                     server_append_caris_file text NOT NULL DEFAULT "False",
                                     km_listen_port integer NOT NULL DEFAULT 16103,
                                     km_listen_timeout integer NOT NULL DEFAULT 1,
                                     sis_auto_apply_manual_casts text NOT NULL DEFAULT "True",
                                     server_apply_surface_sound_speed text NOT NULL DEFAULT "True",
                                     sippican_listen_port integer NOT NULL DEFAULT 16103,
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
                                     CHECK (settings_status IN ("active", "inactive")),
                                     CHECK (ssp_extension_source IN ("RTOFS", "WOA09", "WOA13")),
                                     CHECK (ssp_salinity_source IN ("RTOFS", "WOA09", "WOA13")),
                                     CHECK (ssp_temp_sal_source IN ("RTOFS", "WOA09", "WOA13")),
                                     CHECK (sis_server_source IN ("RTOFS", "WOA09", "WOA13")),
                                     CHECK (ssp_up_or_down IN ("downcast", "upcast")),
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
                                     )
                                  """)

                self.conn.execute("""
                                  CREATE TABLE IF NOT EXISTS client_list(
                                     id integer PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                                     settingsId INTEGER NOT NULL,
                                     name text NOT NULL DEFAULT "Local test",
                                     ip text NOT NULL DEFAULT "127.0.0.1",
                                     port integer NOT NULL DEFAULT 4001,
                                     protocol text NOT NULL DEFAULT "SIS",
                                     FOREIGN KEY(settingsId) REFERENCES general(id),
                                     /* Checks */
                                     CHECK (port > 0),
                                     CHECK (protocol IN ("SIS", "HYPACK", "PDS2000", "QINSY"))
                                     )
                                  """)

                self.conn.execute("""
                                  CREATE VIEW IF NOT EXISTS settings_view AS
                                     SELECT * FROM general g
                                        LEFT OUTER JOIN client_list c
                                        ON g.id=c.settingsId
                                  """)

            return True

        except sqlite3.Error as e:
            log.error("during building tables, %s: %s" % (type(e), e))
            return False

    def check_default_settings(self):
        """ Check for the presence of default settings, adding if missing. """

        try:
            default_settings = "default"
            ret = self.conn.execute("""
                                    SELECT COUNT(id) FROM general WHERE settings_name=?
                                    """, (default_settings, )).fetchone()
            log.info("found %s settings named %s" % (ret[0], default_settings))

            if ret[0] == 0:
                self.add_settings(settings_name=default_settings)

        except sqlite3.Error as e:
            log.error("%s: %s" % (type(e), e))
            return False

    def add_settings(self, settings_name):
        """ Add setting with passed name and default values.

        Args:
            settings_name:              The name of the new settings
        """

        with self.conn:
            try:
                # create a default settings record
                self.conn.execute("""
                                  INSERT INTO general DEFAULT VALUES
                                  """)
                log.info("inserted %s settings with default values" % settings_name)

                # retrieve settings id
                ret = self.conn.execute("""
                                        SELECT id FROM general WHERE settings_name=?
                                        """, (settings_name, )).fetchone()
                log.info("%s settings id: %s" % (settings_name, ret[0]))

                # add default client list
                self.conn.execute("""
                                  INSERT INTO client_list (settingsId) VALUES(?)
                                  """, (ret[0], ))
                log.info("inserted %s settings values" % settings_name)

            except sqlite3.Error as e:
                log.error("%s: %s" % (type(e), e))
                return False