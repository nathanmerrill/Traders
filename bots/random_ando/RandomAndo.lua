--RandomAndo

math.randomseed(os.time()) math.random()math.random()math.random()

ITEMS = {"A", "B", "C","D", "E"}
MARKETOPTION = {"P", "S"}
MyGoods = {0,0,0,0,0}

local function readline() -- checks for the dying "Q" or just reads line
    local line = io.read("*l")
    if line == "Q" then
        os.exit()
    end

    return line
end

local function print(output)
    io.write(output,"\n")
    io.stdout:flush()
end

local function getCurrentTurn() -- asks for M,T,P
    print("T")
    return readline()
end

local function getRandom(array) -- returns for a random element in array
    local r=math.random(#array)
    return array[r]
end

local function getRandomMyItems() -- make a list of items I have and return a random one (no more than one of)
    local rgood=math.random(5)
    local amount=1
    while MyGoods[rgood] <= 0 do
        rgood=math.random(5)
    end
    return amount.."-"..ITEMS[rgood]
end

local function parseGoods(goodString) -- specialized to getMyGoods atm
    local goods={0,0,0,0,0}
    local c = 1
    example = "5-A,6-B,3-C,12-D,4-E"
    for good in goodString:gmatch("%d+%p[ABCDE]") do
        goods[c]=goods[c]+good:match("%d+")
        c=c+1
    end

    return goods
end

local function getMyGoods() -- asks for my goods
    print("G")
    local temp = parseGoods(readline())
    for i=1,5 do
        MyGoods[i]=temp[i]
    end
end


productivity = readline() -- doesn't matter

while true==true do
    print(getRandom(ITEMS)) -- produce random item

    while getCurrentTurn()=="M" do
        getMyGoods()

        local action=getRandom(MARKETOPTION) -- make a random market decision
        if action == "S" then -- offer to sell 1 of a random item I  have in stock, will take any 2 offered
            print("S")
            if readline()=="T" then
                print(getRandomMyItems())
                print("2-A,2-B,2-C,2-D,2-E")
            end
        elseif action == "P" then -- if I can do the deal, I will
            print("P")
            if readline()=="T" then
                local offered=readline()
                local accepted =readline()
                local taccepted={}
                for i in accepted:gmatch("%d+%p[ABCDE]") do
                    oitem =i:match("[ABCDE]")
                    oamount = i:match("%d+")
                    for k=1,5 do
                        if ITEMS[k]==oitem and MyGoods[k]>=tonumber(oamount) then
                            table.insert(taccepted, oitem)
                        end
                    end
                    if #taccepted>=1 then
                        print(getRandom(taccepted))
                    else
                        print("X")
                    end
                end
            end
        elseif action == "L" then
            print("L")
        end
    end
end