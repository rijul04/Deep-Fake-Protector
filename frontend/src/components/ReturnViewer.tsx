import { HStack, Progress, Stack, VStack } from "@chakra-ui/react";
import Card from "./Card";

type Props = {
    oldImg: string;
    newImg: string | undefined;

    predictions: {
        prediction: "FAKE" | "REAL";
        confidence: string;
    }[]

    thresholdLevel: number;
}

export default function ReturnViewer({oldImg, newImg, predictions, thresholdLevel}: Props){

    //  do the below here for now but shld be dont in backend as return
    let totalPred = 0;
    predictions.forEach((pred) => {
        totalPred += Number(parseFloat(pred.confidence.replace("%", "")).toFixed(2));
    })

    const averagePred = totalPred / predictions.length

    return (
        <>
        <Card>
            <h4>Image Preview</h4>
            <Stack direction={{ base: "column", md: "row" }} gap={"2rem"}>
                <img src={oldImg} />
                {newImg && <img src={`data:image/png;base64,${newImg}`} />}
            </Stack>
        </Card>

        <Card>

            <h4>Protection Statistics</h4>
            <Stack direction={{ base: "column", md: "row" }} gap={"2rem"} minW={"50vw"}>
                <div>
                    <h6>AI Detection Level</h6>
                    <Progress colorScheme='purple' size='md' minW={"24vw"} value={averagePred} />
                </div>

                <div>
                    <h6>Protection Threshold Applied</h6>
                    <Progress colorScheme='cyan' size='md' minW={"24vw"} value={thresholdLevel} />
                </div>
            </Stack>
        </Card>
        </>
    )
}