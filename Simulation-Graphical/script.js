/**
 * Created by Robb on 3/16/2016.
 */
var stools = [];
var bartenderImg = 'bartender1.png';
var beerImg = 'beer-icon.png';
var drinkBeingMadeImg = 'drink-make.png';
var serverBeckoningImg = 'server-beckoning.jpg';
var serverPreppedImg = 'server-holding-drink.jpg';
var drinkingBeerImg = 'half-empty-drink.png';
var emptyBeerImg = 'empty-beer.png';
var beerOrderImg = 'beer-order.jpg';
var checkImg = 'guest-check.jpeg';
var isImgDoneLoading = true;
var numServersSeating = 0;
$(function () {
    simulate('bal');
    $("#submit").on('click', function () {
        simulate($('#json').val());
        $("#submit").hide();
        $("#json").hide();
    });
});

function simulate(contents) {
    var canvas = document.getElementById('canvas');
    var ctx = canvas.getContext('2d');

    var customers = [{}];
    var servers = [];
    initQueue(customers);
    initServers(servers);
    let i =0;
    let loop = setInterval(function(){
        //clear all
        ctx.clearRect(0,0,canvas.width,canvas.height);
        //update positions
        randomAction(customers,servers);
        //render
        drawBar(ctx);
        drawStools(ctx);
        drawQueueLine(ctx);
        drawQueueCustomers(ctx,customers);
        drawBarCustomers(ctx,customers);
        drawServers(ctx,servers);
        //actions for next update
        customers = removeDepartingCustomers(customers);
        i++;
        if(i == 200){
            clearInterval(loop);
        }
    },200);
}
function randomAction(customers,servers){
    let queueCustomers = customers
        .filter((cust)=>cust.state=='queue');
    let queueCustomer = null;
    if(queueCustomers.length != 0){
        queueCustomer = queueCustomers[random(0,queueCustomers.length-1)];
    }
    let barCustomer = null;
    let barCustomers = customers
        .filter((cust)=>cust.state=='waiting');
    if(barCustomers.length != 0){
        barCustomer = barCustomers[random(0,barCustomers.length-1)];
    }
    let drinkingCustomer = null;
    let drinkingCustomers = customers
        .filter((cust)=>cust.state=='drinking');
    if(drinkingCustomers.length != 0){
        drinkingCustomer = drinkingCustomers[random(0,barCustomers.length-1)];
    }
    let server = servers[random(0, servers.length - 1)];
    switch(random(1,7)){
        case 1:
        if(barCustomer && server)
                makeDrink(server);
            break;
        case 2:
            if(queueCustomer && server){
                seatCustomer(queueCustomer, server,stoolNum++);
                if(stoolNum == 9)
                    stoolNum = 0;
            }
            break;
        case 3:
            if(barCustomer && server)
                giveDrink(barCustomer,server);
            break;
        case 4:
            if(drinkingCustomer)
                finishDrink(drinkingCustomer);
            break;
        case 5:
            if(barCustomer)
                customerLeaves(barCustomer);
            break;
        case 6:
            customers = customerArrives(customers);
            break;
        case 7:
            if(barCustomer)
                server.setHoldingDrink();
    }
}
var stoolNum = 0;
function customerLeaves(customer){
    customer.depart();
}
function customerArrives(customerQ){
    //in drawQueueCustomers, customers will be updated with proper x,y values
    customerQ.push(new Customer(0, 0));
    return customerQ
}
function finishDrink(customer){
    customer.finishDrink();
}
function giveDrink(customer,server){
    server.setIdle();
    customer.drinkServed();
}
function makeDrink(server){
    server.setPreparingDrink();
}
function seatCustomer(customer,server,stool){
    customer.sitCustomer(stool);
    server.setSeating();
}
function removeDepartingCustomers(customerQ){
    return customerQ.filter((cust) => cust.state != 'departing');
}
function drawStools(ctx) {
    ctx.fillStyle = 'brown';
    for (let i = 0; i < 11; i++) {
        ctx.beginPath();
        ctx.arc(235 + (800 / 10) * i, 200, 25, 0, 2 * Math.PI); //bar stools
        ctx.fill();
        ctx.closePath();
    }
}
function drawQueueLine(ctx) {
    ctx.fillStyle = 'black';
    ctx.fillRect(100, 25, 50, 25 + 75 * 10);
    ctx.fill();

    ctx.clearRect(1010,175, 50,50)
}
function drawBar(ctx) {
    ctx.fillStyle = 'orange';
    ctx.fillRect(200, 100, 800, 50);
    ctx.fill();
}
function drawServers(ctx,servers){
    servers.forEach(function (server) {
        server.render(ctx)
    });
}
function drawBarCustomers(ctx,customers){
    customers
        .filter(function(cust) {return cust.state != 'queue'})
        .forEach(function (cust) {
            cust.render(ctx)
        });
}
function drawQueueCustomers(ctx,customers){
    let i =0;
    customers
        .filter(function(cust) {return cust.state == 'queue'})
        .forEach(function (cust) {
            cust.x = 50;
            cust.y = 50 + 75*i;
            cust.render(ctx);
            i++;
        });
    if(i > 0){
        ctx.font = '24px serif';
        ctx.fillText(i + " customers in queue", 0, 20);
    }
}
function initServers(servers){
    for(let i=0; i< 2; i++){
        servers[i] = new Server(400 + 300 * i,'idle');
    }
}

function initQueue(customerQ) {
    for (let i = 0; i < 5; i++) {
        customerQ[i] = new Customer(50, 50 + 75 * i);
    }
}

class Server{
    constructor(x,state){
        this.x = x;
        this.state = state;
    }
    render(ctx) {
        if (this.state === 'idle') {
            this.bartenderIdle(ctx);
        } else if (this.state === 'drinkMaking') {
            this.bartenderMaking(ctx);
        } else if (this.state === 'seating') {
            this.serveQueue(ctx);
        } else if (this.state === 'drinkDelivery'){
            this.bartenderPreppedDrink(ctx);
        }
    }
    setIdle(){
        if(this.state == 'seating'){
            numServersSeating--;
        }
        this.state = 'idle'
    }
    setPreparingDrink(){
        if(this.state == 'seating'){
            numServersSeating--;
        }
        this.state = 'drinkMaking'
    }
    setSeating(){
        if(this.state != 'seating'){
            this.serverSeatingNumber = numServersSeating;
            numServersSeating++;
        }
        this.state = 'seating'
    }
    setHoldingDrink(){
        if(this.state == 'seating'){
            numServersSeating--;
        }
        if(this.state != 'drinkMaking')
            console.log("Server prepped drink without making it first");
        this.state = 'drinkDelivery';
    }
    serveQueue(ctx) {
        image(ctx, serverBeckoningImg, 100, 25 + 132 * this.serverSeatingNumber);
    }
    bartenderPreppedDrink(ctx){
        image(ctx, serverPreppedImg, this.x + 40, 1)
    }
    bartenderMaking(ctx) {
        image(ctx, drinkBeingMadeImg, this.x + 50, 1)
    }
    bartenderIdle(ctx) {
        image(ctx, bartenderImg, this.x, 1)
    }
}

class Customer {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.color = getRndColor();
        this.state = 'queue';
    }

    render(ctx) {
        draw(ctx, (cxt) => {
            ctx.fillStyle = this.color;
            ctx.arc(this.x, this.y, 25, 0, 2 * Math.PI);
            if(this.state == 'served'){
                this.drawDrink(ctx,beerImg);
                this.state = 'drinking';
            }else if(this.state == 'drinking'){
                this.drawDrink(ctx, drinkingBeerImg);
            }else if(this.state == 'drunk'){
                this.drawDrink(ctx,emptyBeerImg);
                this.state = 'waiting';
            }
            if(this.state == 'waiting'){
                this.drawOrderingBubble(ctx,beerOrderImg);
            } else if(this.state =='departing'){
                this.drawOrderingBubble(ctx, checkImg);
            }
        })
    }
    depart(){
        this.state = 'departing';
    }
    finishDrink(){
        this.state = 'drunk';
    }
    drinkServed(){
        this.state = 'served';
    }
    sitCustomer(stool) {
        this.x = 235+ (800/10) * stool;
        this.y = 200;
        this.state = 'waiting';
    }
    drawDrink(ctx,url) {
        image(ctx, url, this.x - 25, 100);
    }
    drawOrderingBubble(ctx,url){
        image(ctx,url,this.x - 25, 250);
    }
}
function getRndColor() {
    var r = 255 * Math.random() | 0,
        g = 255 * Math.random() | 0,
        b = 255 * Math.random() | 0;
    return 'rgb(' + r + ',' + g + ',' + b + ')';
}
function image(ctx, url, x, y) {
    var img = new Image();
    isImgDoneLoading = false;
    img.onload = function () {
        isImgDoneLoading = true;
        ctx.drawImage(img, x, y);
    };
    img.src = url;
}
function afterImgLoad(ctx, func) {
    setTimeout(function () {
        requestAnimationFrame(function () {
            if (isImgDoneLoading == true) {
                func(ctx);
            } else {
                afterImgLoad(ctx, func);
            }
        })
    }, 10)
}
function draw(ctx, func) {
    ctx.beginPath();
    func(ctx);
    ctx.fill();
    ctx.closePath();
}
function random (min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
};