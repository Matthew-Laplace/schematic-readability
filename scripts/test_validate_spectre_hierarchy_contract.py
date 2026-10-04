"""Offline regression for scalarized netlist and array-rejection boundaries."""

import unittest
from pathlib import Path
from unittest.mock import patch

from validate_spectre_hierarchy_contract import ContractError, parse_netlist, validate


class ScalarizationTests(unittest.TestCase):
    def check_text(self, text, consumers):
        contract = {
            "parent_subckt": "TOP",
            "connections": [{
                "producer": {"instance": "P0", "ports": "Q"},
                "consumers": [{"instance": name, "ports": "D"} for name in consumers],
            }],
        }
        with patch.object(Path, "read_text", return_value=text):
            return validate(parse_netlist(Path("in-memory.scs")), contract)

    def netlist(self, instances, producer_net="EN", consumer_port="D"):
        return (
            "subckt P Q\nends P\n"
            f"subckt C {consumer_port}\nends C\n"
            f"subckt TOP\nP0 ({producer_net}) P\n{instances}\nends TOP\n"
        )

    def test_explicit_scalar_broadcast(self):
        text = self.netlist("C<1> (EN) C\nC<0> (EN) C")
        self.assertEqual(self.check_text(text, ["C<1>", "C<0>"]), [])

    def test_disconnected_broadcast_member(self):
        text = self.netlist("C<1> (EN) C\nC<0> (OTHER) C")
        self.assertTrue(self.check_text(text, ["C<1>", "C<0>"]))

    def test_unlisted_consumer(self):
        text = self.netlist("C0 (EN) C\nC1 (EN) C")
        self.assertTrue(self.check_text(text, ["C0"]))

    def test_device_m_is_not_instance_array(self):
        self.assertEqual(self.check_text(self.netlist("C0 (EN) C m=4"), ["C0"]), [])

    def test_literal_array_must_not_pass(self):
        for name in ("C<1:0>", "C<0:1>", "C<-1:0>", "C<0:1><0>"):
            with self.subTest(name=name), self.assertRaisesRegex(ContractError, "unexpanded"):
                self.check_text(self.netlist(f"{name} (EN) C"), [name])

    def test_escaped_array_must_not_pass(self):
        with self.assertRaisesRegex(ContractError, "unexpanded"):
            self.check_text(self.netlist(r"C\<1:0\> (EN) C"), ["C<1:0>"])

    def test_ranged_net_must_not_pass(self):
        with self.assertRaisesRegex(ContractError, "unexpanded"):
            self.check_text(self.netlist("C0 (EN<1:0>) C", "EN<1:0>"), ["C0"])

    def test_ranged_master_port_is_unsupported(self):
        with self.assertRaisesRegex(ContractError, "unexpanded"):
            self.check_text(self.netlist("C0 (EN) C", consumer_port="D<1:0>"), ["C0"])


if __name__ == "__main__":
    unittest.main()
