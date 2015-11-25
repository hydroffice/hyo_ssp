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
                                     km_listen_port integer NOT NULL DEFAULT 16103,
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
                                     CHECK (settings_status IN ("active", "inactive")),
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

    @property
    def active_settings_id(self):
        # retrieve the active settings id
        ret = self.conn.execute("""
                                SELECT id FROM general WHERE settings_status="active"
                                """).fetchone()
        # log.info("active settings id: %s" % ret[0])
        return ret[0]

    @property
    def rx_max_wait_time(self):
        # rx maximum waiting time
        ret = self.conn.execute("""
                                SELECT rx_max_wait_time FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("rx maximum waiting time: %s" % ret[0])
        return ret[0]

    @property
    def ssp_extension_source(self):
        # SSP extension source
        ret = self.conn.execute("""
                                SELECT ssp_extension_source FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("SSP extension source: %s" % ret[0])
        return ret[0]

    @property
    def ssp_salinity_source(self):
        # SSP salinity extension source
        ret = self.conn.execute("""
                                SELECT ssp_salinity_source FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("SSP salinity extension source: %s" % ret[0])
        return ret[0]

    @property
    def ssp_temp_sal_source(self):
        # SSP temperature and salinity extension source
        ret = self.conn.execute("""
                                SELECT ssp_temp_sal_source FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("SSP temperature and salinity extension source: %s" % ret[0])
        return ret[0]

    @property
    def sis_server_source(self):
        # SIS server source
        ret = self.conn.execute("""
                                SELECT sis_server_source FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("SIS server source: %s" % ret[0])
        return ret[0]

    @property
    def woa_path(self):
        # WOA Path
        ret = self.conn.execute("""
                                SELECT woa_path FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("WOA Path: %s" % ret[0])
        return ret[0]

    @property
    def ssp_up_or_down(self):
        # SSP up or down
        ret = self.conn.execute("""
                                SELECT ssp_up_or_down FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("SSP up or down: %s" % ret[0])
        return ret[0]

    @property
    def user_append_caris_file(self):
        # User append Caris file
        ret = self.conn.execute("""
                                SELECT user_append_caris_file FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Append Caris file (user): %s" % ret[0])
        return ret[0] == "True"

    @property
    def user_export_prompt_filename(self):
        # User export prompt filename
        ret = self.conn.execute("""
                                SELECT user_export_prompt_filename FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Export prompt filename (user): %s" % ret[0])
        return ret[0] == "True"

    @property
    def auto_export_on_send(self):
        # Automatic export SSP of send
        ret = self.conn.execute("""
                                SELECT auto_export_on_send FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Automatic export SSP of send: %s" % ret[0])
        return ret[0] == "True"

    @property
    def server_append_caris_file(self):
        # Server append Caris file
        ret = self.conn.execute("""
                                SELECT server_append_caris_file FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Server append Caris file: %s" % ret[0])
        return ret[0] == "True"

    @property
    def auto_export_on_server_send(self):
        # Server export of server send
        ret = self.conn.execute("""
                                SELECT auto_export_on_server_send FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Server export of server send: %s" % ret[0])
        return ret[0] == "True"

    @property
    def server_apply_surface_sound_speed(self):
        # Server apply surface sound speed
        ret = self.conn.execute("""
                                SELECT server_apply_surface_sound_speed FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Server apply surface sound speed: %s" % ret[0])
        return ret[0] == "True"

    @property
    def km_listen_port(self):
        # KM listen port
        ret = self.conn.execute("""
                                SELECT km_listen_port FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("KM listen port: %s" % ret[0])
        return ret[0]

    @property
    def km_listen_timeout(self):
        # KM Listen Time-out
        ret = self.conn.execute("""
                                SELECT km_listen_timeout FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("KM Listen Time-out: %s" % ret[0])
        return ret[0]

    @property
    def sis_auto_apply_manual_casts(self):
        # SIS automatic apply manual casts
        ret = self.conn.execute("""
                                SELECT sis_auto_apply_manual_casts FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Server apply surface sound speed: %s" % ret[0])
        return ret[0] == "True"

    @property
    def sippican_listen_port(self):
        # Sippican listen port
        ret = self.conn.execute("""
                                SELECT sippican_listen_port FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Sippican listen port: %s" % ret[0])
        return ret[0]

    @property
    def sippican_listen_timeout(self):
        # Sippican listen timeout
        ret = self.conn.execute("""
                                SELECT sippican_listen_timeout FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Sippican listen timeout: %s" % ret[0])
        return ret[0]

    @property
    def mvp_ip_address(self):
        # MVP IP Address
        ret = self.conn.execute("""
                                SELECT mvp_ip_address FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP IP Address: %s" % ret[0])
        return ret[0]

    @property
    def mvp_listen_port(self):
        # MVP listen port
        ret = self.conn.execute("""
                                SELECT mvp_listen_port FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP listen port: %s" % ret[0])
        return ret[0]

    @property
    def mvp_listen_timeout(self):
        # MVP listen timeout
        ret = self.conn.execute("""
                                SELECT mvp_listen_timeout FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP listen timeout: %s" % ret[0])
        return ret[0]

    @property
    def mvp_transmission_protocol(self):
        # MVP transmission protocol
        ret = self.conn.execute("""
                                SELECT mvp_transmission_protocol FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP transmission protocol: %s" % ret[0])
        return ret[0]

    @property
    def mvp_format(self):
        # MVP format
        ret = self.conn.execute("""
                                SELECT mvp_format FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP format: %s" % ret[0])
        return ret[0]

    @property
    def mvp_winch_port(self):
        # MVP winch port
        ret = self.conn.execute("""
                                SELECT mvp_winch_port FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP winch port: %s" % ret[0])
        return ret[0]

    @property
    def mvp_fish_port(self):
        # MVP fish port
        ret = self.conn.execute("""
                                SELECT mvp_fish_port FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP fish port: %s" % ret[0])
        return ret[0]

    @property
    def mvp_nav_port(self):
        # MVP navigation port
        ret = self.conn.execute("""
                                SELECT mvp_nav_port FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP navigation port: %s" % ret[0])
        return ret[0]

    @property
    def mvp_system_port(self):
        # MVP system port
        ret = self.conn.execute("""
                                SELECT mvp_system_port FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP system port: %s" % ret[0])
        return ret[0]

    @property
    def mvp_sw_version(self):
        # MVP SW version
        ret = self.conn.execute("""
                                SELECT mvp_sw_version FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP SW version: %s" % ret[0])
        return float(ret[0])

    @property
    def mvp_instrument(self):
        # MVP instrument
        ret = self.conn.execute("""
                                SELECT mvp_instrument FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP instrument: %s" % ret[0])
        return ret[0]

    @property
    def mvp_instrument_id(self):
        # MVP instrument ID
        ret = self.conn.execute("""
                                SELECT mvp_instrument_id FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("MVP instrument ID: %s" % ret[0])
        return ret[0]

    @property
    def settings_name(self):
        # ssp client
        ret = self.conn.execute("""
                                SELECT settings_name FROM general WHERE id=?
                                """, (self.active_settings_id, )).fetchone()
        log.info("Settings name: %s" % ret[0])
        return ret[0]

    @property
    def client_list(self):
        # ssp client
        ret = self.conn.execute("""
                                SELECT name, ip, port, protocol FROM client_list WHERE settingsId=?
                                """, (self.active_settings_id, )).fetchall()
        log.info("SSP clients: %s" % len(ret))
        return ret
