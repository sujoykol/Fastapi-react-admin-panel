from pathlib import Path

import joblib
import pandas as pd


class MLService:

    def __init__(self):

        base_dir = Path(__file__).resolve().parents[2]

        model_path = (
            base_dir
            / "models"
            / "house_price_model.pkl"
        )

        bundle = joblib.load(model_path)

        self.model = bundle["model"]
        self.location_ppsf = bundle["location_ppsf"]
        self.overall_ppsf = bundle["overall_ppsf"]
        self.floor_median = bundle["floor_median"]
        self.encoder = bundle["encoder"]

    def predict(
        self,
        BHK: int,
        Super_Area_SQFT: float,
        Floor: float | None,
        Bathroom: int,
        Garden_Park: int,
        Main_Road: int,
        Pool: int,
        Address: str,
    ) -> dict:

        property_df = pd.DataFrame([
            {
                "BHK": BHK,
                "Super Area(SQFT)": Super_Area_SQFT,
                "Floor": Floor,
                "Bathroom": Bathroom,
                "Garden/Park": Garden_Park,
                "Main Road": Main_Road,
                "Pool": Pool,
                "Address": Address,
            }
        ])

        property_df["Floor"] = (
            property_df["Floor"]
            .fillna(self.floor_median)
        )

        property_df["Is_Ground_Floor"] = (
            property_df["Floor"] == 0
        ).astype(int)

        def get_floor_band(floor):

            if floor == 0:
                return "Ground"

            elif floor <= 4:
                return "Low"

            elif floor <= 9:
                return "Mid"

            return "High"

        property_df["Floor_Band"] = (
            property_df["Floor"]
            .apply(get_floor_band)
        )

        property_df["Location_PPSF"] = (
            property_df["Address"]
            .map(self.location_ppsf)
            .fillna(self.overall_ppsf)
        )

        model_features = [
            "BHK",
            "Super Area(SQFT)",
            "Floor",
            "Bathroom",
            "Garden/Park",
            "Main Road",
            "Pool",
            "Is_Ground_Floor",
        ]

        property_model = property_df[
            model_features
        ].copy()

        floor_encoded = self.encoder.transform(
            property_df[["Floor_Band"]]
        )

        floor_columns = (
            self.encoder.get_feature_names_out(
                ["Floor_Band"]
            )
        )

        floor_encoded = pd.DataFrame(
            floor_encoded,
            columns=floor_columns,
        )

        property_model = pd.concat(
            [
                property_model.reset_index(drop=True),
                floor_encoded.reset_index(drop=True),
            ],
            axis=1,
        )

        property_model["Location_PPSF"] = (
            property_df["Location_PPSF"].values
        )

        prediction_lakh = self.model.predict(
            property_model
        )[0]

        prediction_inr = prediction_lakh * 100000

        return {
            "predicted_price_lakh": round(
                float(prediction_lakh),
                2,
            ),
            "predicted_price_inr": round(
                float(prediction_inr),
                2,
            ),
        }