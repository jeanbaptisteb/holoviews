import numpy as np

from holoviews.core import Overlay, NdOverlay, DynamicMap, HoloMap
from holoviews.element import Curve, Scatter

from .testplot import TestMPLPlot, mpl_renderer

try:
    from holoviews.plotting.mpl import OverlayPlot
except:
    pass


class TestOverlayPlot(TestMPLPlot):

    def test_interleaved_overlay(self):
        """
        Test to avoid regression after fix of https://github.com/ioam/holoviews/issues/41
        """
        o = Overlay([Curve(np.array([[0, 1]])) , Scatter([[1,1]]) , Curve(np.array([[0, 1]]))])
        OverlayPlot(o)

    def test_overlay_empty_layers(self):
        overlay = Curve(range(10)) * NdOverlay()
        plot = mpl_renderer.get_plot(overlay)
        self.assertEqual(len(plot.subplots), 1)

    def test_overlay_update_plot_opts(self):
        hmap = HoloMap(
            {0: (Curve([]) * Curve([])).options(title_format='A'),
             1: (Curve([]) * Curve([])).options(title_format='B')}
        )
        plot = mpl_renderer.get_plot(hmap)
        self.assertEqual(plot.handles['title'].get_text(), 'A')
        plot.update((1,))
        self.assertEqual(plot.handles['title'].get_text(), 'B')

    def test_overlay_update_plot_opts_inherited(self):
        hmap = HoloMap(
            {0: (Curve([]).options(title_format='A') * Curve([])),
             1: (Curve([]).options(title_format='B') * Curve([]))}
        )
        plot = mpl_renderer.get_plot(hmap)
        self.assertEqual(plot.handles['title'].get_text(), 'A')
        plot.update((1,))
        self.assertEqual(plot.handles['title'].get_text(), 'B')

    def test_overlay_apply_ranges_disabled(self):
        overlay = (Curve(range(10)) * Curve(range(10))).options('Curve', apply_ranges=False)
        plot = mpl_renderer.get_plot(overlay)
        self.assertTrue(all(np.isnan(e) for e in plot.get_extents(overlay, {})))

    def test_overlay_empty_element_extent(self):
        overlay = Curve([]).redim.range(x=(-10, 10)) * Scatter([]).redim.range(y=(-20, 20))
        plot = mpl_renderer.get_plot(overlay)
        extents = plot.get_extents(overlay, {})
        self.assertEqual(extents, (-10, -20, 10, 20))

    def test_dynamic_subplot_remapping(self):
        # Checks that a plot is appropriately updated when reused
        def cb(X):
            return NdOverlay({i: Curve(np.arange(10)+i) for i in range(X-2, X)})
        dmap = DynamicMap(cb, kdims=['X']).redim.range(X=(1, 10))
        plot = mpl_renderer.get_plot(dmap)
        plot.update((3,))
        for i, subplot in enumerate(plot.subplots.values()):
            self.assertEqual(subplot.cyclic_index, i+3)
            self.assertEqual(list(subplot.overlay_dims.values()), [i+1])

    def test_dynamic_subplot_creation(self):
        def cb(X):
            return NdOverlay({i: Curve(np.arange(10)+i) for i in range(X)})
        dmap = DynamicMap(cb, kdims=['X']).redim.range(X=(1, 10))
        plot = mpl_renderer.get_plot(dmap)
        self.assertEqual(len(plot.subplots), 1)
        plot.update((3,))
        self.assertEqual(len(plot.subplots), 3)
        for i, subplot in enumerate(plot.subplots.values()):
            self.assertEqual(subplot.cyclic_index, i)
