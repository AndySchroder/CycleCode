package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;

public class ExportCFDyPluscsvFiles extends StarMacro {

	public void execute() {
		execute0();
	}

	private void execute0() {
		Simulation simulation_0 = getActiveSimulation();

		// can't figure out how to get starccm+ to accept a variable on the command line or figure out what it's current simulation name is,
		// so just export to static filenames and then immediately rename with the calling python script after this script exits.

		XYPlot xYPlot_0 = ((XYPlot) simulation_0.getPlotManager().getPlot("y+"));
		xYPlot_0.export(resolvePath("exported_data/y+.csv"), ",");
	}
}



