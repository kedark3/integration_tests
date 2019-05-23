# -*- coding: utf-8 -*-
from time import sleep

from selenium.webdriver.support import expected_conditions
from widgetastic_patternfly import Modal

from cfme.utils.wait import TimedOutError
from cfme.utils.wait import wait_for


class HandleModalsMixin(object):
    @property
    def _modal_alert(self):
        return Modal(parent=self)

    def get_alert(self):
        """Returns the current alert object.

        Raises:
            :py:class:`selenium.common.exceptions.NoAlertPresentException`
        """
        if not self.handles_alerts:
            return None
        modal = self._modal_alert
        return modal if modal.is_displayed else self.selenium.switch_to_alert()

    def handle_alert(self, cancel=False, wait=30.0, squash=False, prompt=None, check_present=False):
        """Handles an alert popup.

        Args:
            cancel: Whether or not to cancel the alert.
                Accepts the Alert (False) by default.
            wait: Time to wait for an alert to appear.
                Default 30 seconds, can be set to 0 to disable waiting.
            squash: Whether or not to squash errors during alert handling.
                Default False
            prompt: If the alert is a prompt, specify the keys to type in here
            check_present: Does not squash
                :py:class:`selenium.common.exceptions.NoAlertPresentException`

        Returns:
            ``True`` if the alert was handled, ``False`` if exceptions were
            squashed, ``None`` if there was no alert.

        No exceptions will be raised if ``squash`` is True and ``check_present`` is False.

        Raises:
            :py:class:`wait_for.TimedOutError`: If the alert popup does not appear
            :py:class:`selenium.common.exceptions.NoAlertPresentException`: If no alert is present
                when accepting or dismissing the alert.
        """
        if not self.handles_alerts:
            return None

        modal = self._modal_alert

        def _check_alert_present():
            if modal.is_displayed:
                # infinispinner if accept button is clicked too quick in  modal
                # BZ(1713399)
                sleep(1)
                return modal
            return expected_conditions.alert_is_present()

        # throws timeout exception if not found
        try:
            if wait:
                wait_for(lambda: _check_alert_present, num_sec=wait)

            popup = self.get_alert()
            self.logger.info('handling alert: %r', popup.text)
            if prompt is not None:
                self.logger.info('  answering prompt: %r', prompt)
                if isinstance(popup, Modal):
                    popup.fill(prompt)
                else:
                    popup.send_keys(prompt)
            if cancel:
                self.logger.info('  dismissing')
                popup.dismiss()
            else:
                self.logger.info('  accepting')
                popup.accept()
            # Should any problematic "double" alerts appear here, we don't care, just blow'em away.
            self.dismiss_any_alerts()
            return True
        except TimedOutError:
            if check_present:
                raise
            else:
                return None
        except Exception:
            if squash:
                return False
            else:
                raise