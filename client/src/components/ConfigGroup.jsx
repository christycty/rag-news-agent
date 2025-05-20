
function ConfigItem({ item_name, item_value } ) {
    return (
        <div className="flex justify-between pr-10 pl-5 py-1 font-mono">
            <div className="">
                {item_name}
            </div>
            <div>
                {item_value}
            </div>
        </div>
    )
}

function UppercaseFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}


export default function ConfigGroup({ group_name, group_content }) {
    return (
        <div className="py-3">
            <div className="text-l font-semibold">
                {"<" + UppercaseFirstLetter(group_name) + ">"}
            </div>
            <div>
                {Object.entries(group_content).map(([item_name, item_value]) => (
                    <ConfigItem key={item_name} item_name={item_name} item_value={item_value} />
                ))}
            </div>
        </div>
    )

}